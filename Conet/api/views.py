import datetime
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View, generic
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q


from Accounts.models import Author
from Accounts.models import Friendship
from posting.models import Post
from posting.serializers import PostSerializer

from .serializers import FollowingSerializers, FollowerSerializers, ExtendAuthorSerializers

from rest_framework.response import Response

# Create your views here.

# api for /author
class AuthorAPI(APIView):
    model = Author

    def get(self, request,*args, **kwargs):
        response = {"query":'author'}
        try:
            # get current user
            current_user = Author.objects.get(id=kwargs['pk'])
            
            # get current user's data. Note that friends' data is excluded
            author_data = ExtendAuthorSerializers(current_user).data
            
            # append each data to response
            for i in author_data.keys():
                response[i] = author_data[i]

            # get people who is followed by current user.
            followings = FollowingSerializers(current_user).data['friends']
            
            # get people who is following current user
            followers = FollowerSerializers(current_user).data['follower']

            # parse result from serializers. following_id will be a list of strings of UUID
            following_id = []
            for f in followings:
                following_id.append(str(f['author']))
            follower_id = []
            for f in followers:
                follower_id.append(str(f['author']))
            
            # find who is both followed by current user and following current user
            friends = list(set(following_id) & set(follower_id))
            
            # append friend's detailed information to response
            response['friends'] = []
            for friend in friends:
                friend_data = ExtendAuthorSerializers(Author.objects.get(id=friend)).data 
                response['friends'].append(json.dumps(friend_data))
            return Response(response, status=200)
        except:
            response['authors'] = []
            return Response(response, status=400)


# /unfriendrequest
# getting POST request from client. Un-friend given initiator and receiver.
def unfriend_request(request):
    # only accepting POST method
    if request.method == 'POST':
        # parse request body
        request_body = json.loads(request.body.decode())

        # instanciate initiator and receiver as Author object
        init_user = Author.objects.get(id=request_body['author']['id'])
        recv_user = Author.objects.get(id=request_body['friend']['id'])
        response = {"query":'unfriendrequest'}
        response['message'] = 'Unfriend request received'

        # try to delete the relationship with given init_user and recv_user
        try:
            Friendship.objects.filter(init_id=init_user, recv_id=recv_user).delete()    # pylint: disable=maybe-no-member
            response['success'] = True
            return HttpResponse(json.dumps(response), 200)
        except:
            response['success'] = False
            return HttpResponse(json.dumps(response), status=400)
    else:
        response={"Access-Control-Allow-Methods": 'POST'}
        return HttpResponse(json.dumps(response), status=405)

# /friendrequest
def friend_request(request):
    if request.method == 'POST':
        # parse request body
        request_body = json.loads(request.body.decode())

        # instanciate initiator and receiver as Author object
        init_user = Author.objects.get(id=request_body['author']['id'])
        recv_user = Author.objects.get(id=request_body['friend']['id'])
        response = {"query":'friendrequest'}
        response['message'] = 'Friend request received'
        # try to add the relationship with given init_user and recv_user
        try: 
            friendship = Friendship(init_id=init_user, recv_id=recv_user, starting_date=datetime.datetime.now(), status=0)
            friendship.save()
            response['success'] = True
            return HttpResponse(json.dumps(response), 200)
        except:
            response['success'] = False
            return HttpResponse(json.dumps(response), status=400)
    else:
        response={"Access-Control-Allow-Methods": 'POST'}
        return HttpResponse(json.dumps(response), status=405)


# for author/{author_id}/following
# getting who is following current user
class AuthorFollowing(View):
    model=Author
    # get a list of author's following authors
    def get(self, request,*args, **kwargs):
        response = {"query":'friends'}
        try:
            # get current user based on URL on browser. It is the id of user who is currently being viewed.
            current_user = Author.objects.get(id=kwargs['pk'])

            # get people whom this user is following.
            followings = FollowingSerializers(current_user).data['friends']
            response['authors'] = []

            # append each friend's id to a list. For response
            for friend in followings:
                response['authors'].append(str(friend['author']))
            return HttpResponse(json.dumps(response), 200)
        except:
            response['authors'] = []
            return HttpResponse(json.dumps(response), 400)


# for author/{author_id}/follower
class AuthorFollower(APIView):
    model=Author
    
    # get a list of author's followers
    def get(self, request,*args, **kwargs):
        response = {"query":'friends'}
        try:
            # get current user based on URL on browser. It is the id of user who is currently being viewed.
            current_user = Author.objects.get(id=kwargs['pk'])
            # get people who is following the user shows on screen.
            followers = FollowerSerializers(current_user).data['follower']
            response['authors'] = []
            for friend in followers:
                response['authors'].append(str(friend['author']))
            return Response(response)
        except:
            response['authors'] = []
            return Response(response, status=400)
    

# for api/author/{author_id}/friends
class AuthorFriends(APIView):
    # get a list of ids who is friend of given user.
    def get(self, request,*args, **kwargs):
        response = {"query":'friends'}
        try:
            # get current user on URL
            current_user = Author.objects.get(id=kwargs['pk'])

            # get a list of followers and list of people whom current user is following.
            followings = FollowingSerializers(current_user).data['friends']
            followers = FollowerSerializers(current_user).data['follower']
            
            # parse result to list
            following_id = []
            for f in followings:
                following_id.append(str(f['author']))

            follower_id = []
            for f in followers:
                follower_id.append(str(f['author']))
            
            # find who is both followed by current user and following current user
            friends = list(set(following_id) & set(follower_id))
            response['authors'] = friends
            return Response(response)
        except:
            response['authors'] = []
            return Response(response, status=400)
    
    # Ask a service if anyone in the list is a friend
    def post(self, request,*args, **kwargs):
        # parse request body
        request_body = json.loads(request.body.decode())

        # get the authors who are checked be a friend of author shows in URL
        request_friends = request_body['authors']
        for friend in request_friends:
            friend = str(friend)
        response = {"query":'friends'}
        try:
            # get current user on URL
            current_user = Author.objects.get(id=kwargs['pk'])
            
            # get a list of followers and list of people whom current user is following.
            followings = FollowingSerializers(current_user).data['friends']
            followers = FollowerSerializers(current_user).data['follower']
            
            # parse result to list
            following_id = []
            for f in followings:
                following_id.append(str(f['author']))
            follower_id = []
            for f in followers:
                follower_id.append(str(f['author']))
            # find who is both followed by current user and following current user
            friends = list(set(following_id) & set(follower_id))
            response['authors'] = []
            for friend in friends:
                if str(friend) in request_friends:
                    response['authors'].append(str(friend))
            return Response(response)
        except:
            response['authors'] = []
        return Response(response, status=400)

#reference: https://docs.djangoproject.com/en/2.1/ref/request-response/

# service/author/<authorid>/friends/<authorid>
class TwoAuthorsRelation(APIView):
    def get(self, request, author_id1, author_id2):
        response = {}
        response['query'] = 'friends'
        try:
            author1 = Author.objects.get(id=author_id1)
            author2 = Author.objects.get(id=author_id2)
            followings = FollowingSerializers(author1).data['friends']
            followers = FollowerSerializers(author1).data['follower']
                
            following_id = []
            for f in followings:
                following_id.append(str(f['author']))

            follower_id = []
            for f in followers:
                follower_id.append(str(f['author']))
                
            friends = list(set(following_id) & set(follower_id))
            
            response['friends'] = author_id2 in friends
            response['authors'] = [author1.url, author2.url]
            return Response(response, status=200)
        except:
            response['friends'] = False
            response['authors'] = ["",""]
            return Response(response, status=400)

# service/author/posts
class AuthorizedPostsHandler(APIView):
    def get(self, request):
        allposts = []

        #get the posts of all your friends whos visibility is set to FRIENDS
        curAuthor = request.user.id
        relations = Friendship.objects.filter(init_id = curAuthor, status = 1)
        for relation in relations:
            friend_id = relation.recv_id          
            posts = Post.objects.filter(postid = friend_id, visibility = "FRIENDS")
            for i in posts:
                allposts.append(i)
        
        #get all publics posts
        public = Post.objects.filter(visibility="PUBLIC")
        for x in public:
            allposts.append(x)
        
        serializer = PostSerializer(allposts, many=True)
        return Response(serializer.data)


