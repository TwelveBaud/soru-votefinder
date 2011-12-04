from django.conf.urls.defaults import *
from votefinder.main.feeds import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('votefinder.main.views',
    (r'^$',                                     'index'),
    (r'^add$',                                  'add'),
    (r'^add_game/(?P<threadid>\d+)/*$',      	'add_game'),
    (r'^game_list/(?P<page>\d+)/*$',            'game_list'),
    (r'^game/(?P<slug>[\w-]+)$',               	'game'),
    (r'^player/(?P<slug>[\w-]+)/*$',            'player'),
    (r'^p:(?P<playerid>\d+)/*$',                'player_id'),
    (r'^profile/*$',                            'profile'),
    (r'^update/(?P<gameid>\d+)/*$',             'update'),
    (r'^player_state/(?P<gameid>\d+)/(?P<playerid>\d+)/(?P<state>\w+)/$', 'player_state'),
    (r'^player_list/',                          'player_list'),
    (r'^add_player/(?P<gameid>\d+)/*$',         'add_player'),
    (r'^delete_spectators/(?P<gameid>\d+)/*$',  'delete_spectators'),
    (r'^votecount/(?P<gameid>\d+)/*$',          'votecount'),
    (r'^resolve/(?P<voteid>\d+)/(?P<resolution>-{0,1}\d+)/*$', 'resolve'),
    (r'^posts/(?P<gameid>\d+)/(?P<page>\d+)/*$','posts'),
    (r'^add_comment/(?P<gameid>\d+)/*$',        'add_comment'),
    (r'^delete_comment/(?P<commentid>\d+)/*$', 	'delete_comment'),
    (r'^rss/*$',                                LatestRss()),
    (r'^atom/*$',                               LatestAtom()),
    (r'^game_status/(?P<slug>[\w-]+)/*',        SpecificGameStatusAtom()),
    (r'^game_status/*$',                        GameStatusAtom()),
    (r'^faq/*$',                                direct_to_template, {'template': 'faq.html' }),
    (r'^deadline/(?P<gameid>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/(?P<year>[\d]+)/(?P<hour>[\d]+)/(?P<min>[\d]+)/(?P<ampm>[\w]+)/(?P<tzname>.+)$', 'deadline'),
    (r'^close_game/(?P<gameid>\d+)/*$',         'close_game'),
    (r'^reopen_game/(?P<gameid>\d+)/*$',        'reopen_game'),
    (r'^new_day/(?P<gameid>\d+)/(?P<day>\d+)/*$', 'new_day'),
    (r'^replace/(?P<gameid>\d+)/(?P<clear>\w+)/(?P<outgoing>\d+)/(?P<incoming>.+)*$', 'replace'),
    (r'^startday:(?P<day>\d+)/(?P<postid>\d+)*$','start_day'),   
    (r'^templates$',                            'templates'),
    (r'^create_template$',                      'create_template'),
    (r'^template/(?P<templateid>\d+)$',         'edit_template'),
    (r'^delete_template/(?P<templateid>\d+)$',  'delete_template'),
    (r'^game_template/(?P<gameid>\d+)/(?P<templateid>\d+)', 'game_template'),
    (r'^active_games$',                         'active_games'),
    (r'^active_games/json$',                    'active_games_json'),
    (r'^active_games/(?P<style>.+)',            'active_games_style'),
    (r'^closed/*$',                             'closed_games'),
    (r'^add_vote/(?P<gameid>\d+)/(?P<player>[\d-]+)/(?P<votes>\w+)/(?P<target>\d+)$', 'add_vote'),
    (r'^delete_vote/(?P<voteid>\d+)$',          'delete_vote'),
    (r'^img/(?P<slug>[\w-]+)/*$',               'votecount_image'),
    (r'^autoupdate$',                           'autoupdate'),
    (r'^players$',                              'players'),
    (r'^players/(?P<page>\d+)$',                'players_page'),
    (r'^delete_alias/(?P<id>\d+)$',             'delete_alias'),
    (r'^sendpms/(?P<slug>[\w-]+)$',             'sendpms'),
    (r'^post_histories/(?P<gameid>\d+)$',       'post_histories'),
    (r'^post_lynches/(?P<gameid>\d+)/(?P<enabled>\w+)$', 'post_lynches'),
    (r'^post_vc/(?P<gameid>\d+)$',              'post_vc'),
    (r'^rate/(?P<gameid>\d+)/(?P<score>[1-5])', 'rate'),
    (r'^votechart/(?P<gameslug>[\w-]+)$',       'votechart_all'),
    (r'^votechart/(?P<gameslug>[\w-]+)/(?P<playerslug>[\w-]+)$', 'votechart_player'),
    
)
