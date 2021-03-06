from ForumPageDownloader import ForumPageDownloader
import re

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import Comment
from votefinder.main.models import *

class GameListDownloader():
	def __init__(self):
		self.GameList = []
		self.downloader = ForumPageDownloader()
		
	def GetGameList(self, page):
		data = self.DownloadList(page)
		if not data:
			return False
		
		if not self.ParseGameList(data):
			return False
		
		return True
	
	def DownloadList(self, page):
		return self.downloader.download("http://forums.somethingawful.com/forumdisplay.php?forumid=103&pagenumber=%s" % page)
	
	def ParseGameList(self, data):
		soup = BeautifulSoup(data)
		
		for thread in soup.findAll("a", "thread_title"):
			if thread.text.lower().find("mafia") != -1:
				game = {'name': thread.text, 'url': thread["href"], 'tracked': self.IsGameTracked(thread["href"])}
				self.GameList.append(game)
				
		return True
	
	def IsGameTracked(self, url):
		matcher = re.compile("threadid=(?P<threadid>\d+)").search(url)
		if matcher:
			try:
				game = Game.objects.all().get(threadId=matcher.group('threadid'))
				return True
			except Game.DoesNotExist:
				pass
			
		return False
		