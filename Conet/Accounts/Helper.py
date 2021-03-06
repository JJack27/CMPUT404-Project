from rest_framework.response import Response
from posting.models import Post, Comment
from Accounts.models import Author
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, Http404


''' VERIFICATION HELPER START'''

# Verify if the current user has access to post
def currentPostUserVerification(post, request):
    author = post.author_id
    visibility = post.visibility
    unlisted = post.unlisted
    if Author.objects.filter(pk=request.user.id).exists():
        user = Author.objects.get(pk=request.user.id)
        # TODO: Check if user is friends with poster
        if user == author:
            return True
        else:
            if visibility == 'PUBLIC':
                return True
            elif visibility == 'FOAF':
                return True
            #TODO: Check for friend
            elif visibility == 'PRIVATE':
                if user == author:
                    return True
                elif post.visibleTo is not None:
                    if (str(user) in post.visibleTo):
                        return True
                    else:
                        return False
                else:
                    return False
            #TODO: SERVER ONLY
            else:
                    return False
    elif (not User.objects.filter(pk=request.user.id).exists()):
        return False


''' VERIFICATION HELPER END'''


'''VIEW HELPER START'''
def createPost(request):
    return render(request, "createpost.html")

def viewPost(request):
    post_id = 'cf288e8c-89bb-45d4-918d-da16d8e5cda0'
    #comments = Comment.objects.filter(comment_post_id=post_id)
    post = Post.objects.get(pk=post_id)
    verification = currentPostUserVerification(post, request)

    if verification:
        if post.contentType == "image/png;base64" or post.contentType == "image/jpeg;base64":
            pictureContent = True
        else:
            pictureContent = False

        return render(request, "viewpost.html", {
                                         'pictureContent': pictureContent,
                                         'post':post
                                             })
    else:
        raise Http404("Post not found")
''' VIEW HELPER END '''
