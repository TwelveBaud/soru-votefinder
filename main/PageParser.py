import re
import time
from datetime import datetime

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import Comment
from votefinder.main.models import *
from ForumPageDownloader import ForumPageDownloader

class PageParser:
	def __init__(self):
		self.pageNumber = 0
		self.maxPages = 0
		self.gameName = ""
		self.posts = []
		self.players = []
		self.gamePlayers = []
		self.votes = []
		self.user = None
		self.downloader = ForumPageDownloader()
    
	def Add(self, threadid):
		self.new_game = True
		return self.DownloadAndUpdate("http://forums.somethingawful.com/showthread.php?threadid=%s" % threadid, threadid)
		
	def DownloadAndUpdate(self, url, threadid):
		data = self.DownloadForumPage(url)
		if not data:
			return None
		
		game = self.ParsePage(data, threadid)
		if not game:
			return None
		
		return game
	
	def Update(self, game):
		self.new_game = False
		page = game.currentPage
		if game.currentPage < game.maxPages:
			page = game.currentPage + 1
			
		return self.DownloadAndUpdate("http://forums.somethingawful.com/showthread.php?threadid=%s&pagenumber=%s" % (game.threadId, page), game.threadId)

	def DownloadForumPage(self, url):	
		return self.downloader.download(url)
	
	def AutoResolveVote(self, text):
		try:
			player = Player.objects.get(name__iexact=text)
			if player in self.players or player in self.gamePlayers:
				return player
		except Player.DoesNotExist:
			pass
		
		try:
			aliases = Alias.objects.filter(alias__iexact=text, player__in=self.players)
			if len(aliases) > 0:
				return aliases[0].player
		except Alias.DoesNotExist:
			pass

		try:
			aliases = Alias.objects.filter(alias__iexact=text, player__in=self.gamePlayers)
			if len(aliases) > 0:
				return aliases[0].player
		except Alias.DoesNotExist:
			pass
		
		try:
			if len(text) > 4:
				players = Player.objects.filter(name__icontains=text, name__in=[p.name for p in self.gamePlayers])
				if len(players) == 1:
					return players[0]
		except Player.DoesNotExist:
			pass

		return None
	
	def SearchLineForVotes(self, post, line):
		pattern = re.compile("##\\s*unvote|##\\s*vote[:\\s+]([^<\\r\\n]+)", re.I)
		pos = 0
		match = pattern.search(line, pos)

		while match:
			v = Vote(post=post, game=post.game, author=post.author, unvote=True)
			(targetStr, ) = match.groups()
			if targetStr:
				v.targetString = targetStr.strip()
				v.target = self.AutoResolveVote(v.targetString)
				v.unvote = False

				if v.target == None and (v.targetString.lower() == "nolynch" or v.targetString.lower() == "no lynch"):
					v.nolynch = True

			v.save()
			match = pattern.search(line, match.end())
	
	def ReadVotes(self, post):
		for bold in post.bodySoup.findAll("b"):
			content = "".join([str(x) for x in bold.contents])
			for line in content.splitlines():
				self.SearchLineForVotes(post, line) 
	
	def ParsePage(self, data, threadid):
		data = data.replace("<i>", "").replace("</i>", "")
		soup = BeautifulSoup(data)
		
		self.pageNumber = self.FindPageNumber(soup)
		self.maxPages = self.FindMaxPages(soup)
	   	self.gameName = re.compile(r"\[.*?\]").sub("", self.ReadThreadTitle(soup)).strip()

		posts = soup.findAll("table", "post")
		if not posts:
			return None
		
		mod = None
		for postNode in posts:
			newPost = self.ReadPostValues(postNode)
			if newPost:
				if not mod:
					mod = newPost.author

				newPost.pageNumber = self.pageNumber
				self.posts.append(newPost)
	
		game, gameCreated = Game.objects.get_or_create(threadId=threadid,
                  defaults={'moderator': mod, 'name': self.gameName, 'currentPage': 1, 'maxPages': 1, 'added_by': self.user})
		
		if gameCreated:
			playerState, created = PlayerState.objects.get_or_create(game=game, player=mod,
																	 defaults={'moderator': True})
		else:
			self.gamePlayers = [p.player for p in game.all_players()]			
			
		game.maxPages = self.maxPages
		game.currentPage = self.pageNumber
		game.gameName = self.gameName
		
		for post in self.posts:
			post.game = game
			post.save()

			self.ReadVotes(post)

			if not post.author in self.players:
				self.players.append(post.author)

		if self.new_game or self.pageNumber == 1:
			defaultState = 'alive'
		else:
			defaultState = 'spectator'
			
		for player in self.players:
			playerState, created = PlayerState.objects.get_or_create(game=game, player=player,
																     defaults={defaultState: True})

		if gameCreated:
			gameday = GameDay(game=game, dayNumber=1, startPost=self.posts[0])
			gameday.save()

		game.save()		
		return game
	
	def FindPageNumber(self, soup):
		pages = soup.find("div", "pages")
		if pages:
			curPage = pages.find(attrs={"selected":"selected"})
			if curPage:
				return curPage['value']
			else:
				return "1"

		return "1"
	
	def FindMaxPages(self, soup):
		pages = soup.find("div", "pages")
		if pages:
			option_tags = pages.findAll("option")
			total_pages = len(option_tags)
			if total_pages == 0:
				return 1
			else:
				return total_pages
		else:
			return 1
	
	def ReadThreadTitle(self, soup):
		title = soup.find("title")
		if title:
			return title.text[:len(title.text) - 29]
		else:
			return None

	def FindOrCreatePlayer(self, playerName, playerUid):
		player, created = Player.objects.get_or_create(uid=playerUid,
                  defaults={'name': playerName})

		if player.name != playerName:
			player.name = playerName
			player.save()
			
		return player

	def ReadPostValues(self, node):
		postId = node["id"][4:]
		if postId == '':
			return None
		
		try:
			post = Post.objects.get(postId=postId)
			return None
		except Post.DoesNotExist:
			post = Post()
		
		post.postId = postId
		titleNode = node.find("dd", "title")
		if titleNode:
			post.avatar = unicode(titleNode.find("img"))
				
		post.bodySoup = node.find("td", "postbody") 
		[quote.extract() for quote in post.bodySoup.findAll("div", "bbc-block")]
		[img.extract() for img in post.bodySoup.findAll("img")]
		[comment.extract() for comment in post.bodySoup.findAll(text=lambda text:isinstance(text, Comment))]
		post.body = "".join([str(x) for x in post.bodySoup.contents]).strip() 
		
		postDateNode = node.find("td", "postdate")
		if postDateNode:
			dateText = postDateNode.text.replace("#", "").replace("?", "").strip()
			post.timestamp = datetime(*time.strptime(dateText, "%b %d, %Y %H:%M")[:6])
		else:
			return None

		anchorList = postDateNode.findAll("a")
		if len(anchorList) > 0:
			post.authorSearch = anchorList[-1]["href"]

		authorString = node.find("dt", "author").text
		authorString = re.sub("<.*?>", "", authorString)
		authorString = re.sub("&\\w+?;", "", authorString).strip()

		matcher = re.compile("userid=(?P<uid>\d+)").search(post.authorSearch)
		if matcher:
			authorUid = matcher.group('uid')
		else:
			return None

		if authorString == "Adbot":
			return None
		else:
			post.author = self.FindOrCreatePlayer(authorString, authorUid)

		return post
	
