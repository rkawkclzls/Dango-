from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.paginator import Paginator
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib import messages

from .models import Board, Comment
from .forms import BoardForm, CommentForm
from accounts.models import User
from tag.models import Tag

# 새로운 게시글 작성을 처리하는 클래스
class BoardWriteView(View):
    def get(self, request):
        # 사용자가 로그인하지 않은 경우 로그인 페이지로 리다이렉트
        if not request.session.get('user'):
            return redirect('/accounts/login')
        form = BoardForm()
        return render(request, 'boards/board_write.html', {'form': form})

    def post(self, request):
        # 사용자가 로그인하지 않은 경우 로그인 페이지로 리다이렉트
        if not request.session.get('user'):
            return redirect('/accounts/login')
        form = BoardForm(request.POST)
        if form.is_valid():
            user_id = request.session.get('user')
            user = User.objects.get(pk=user_id)
            tags = form.cleaned_data['tags'].split(',')

            # 새로운 게시글 객체를 생성하고 데이터베이스에 저장
            board = Board()
            board.title = form.cleaned_data['title']
            board.contents = form.cleaned_data['contents']
            board.writer = user
            board.save()

            # 태그를 생성하거나 가져와서 게시글과 연결
            for tag in tags:
                if not tag:
                    continue
                _tag, _ = Tag.objects.get_or_create(name=tag)
                board.tags.add(_tag)

            return redirect('/boards/list')
        return render(request, 'boards/board_write.html', {'form': form})

# 게시글 상세 정보를 표시하는 클래스
class BoardDetailView(View):
    def get(self, request, pk):
        # 주어진 기본 키로 게시글 객체를 가져옴
        board = get_object_or_404(Board, pk=pk)
        comments = CommentForm()
        comment_view = Comment.objects.filter(post=pk)
        return render(request, 'boards/board_detail.html', {'board': board, 'comments': comments, 'comment_view': comment_view})

# 게시글 목록을 표시하는 클래스
class BoardListView(View):
    def get(self, request):
        # 모든 게시글 객체를 가져와서 ID를 기준으로 내림차순으로 정렬
        all_boards = Board.objects.all().order_by('-id')
        page = int(request.GET.get('p', 1))
        paginator = Paginator(all_boards, 5)
        boards = paginator.get_page(page)
        user_id = request.session.get('user')
        user = User.objects.get(pk=user_id)
        return render(request, 'boards/board_list.html', {'boards': boards, 'username': user.username})

# 게시글을 업데이트하는 클래스
class BoardUpdateView(UpdateView):
    model = Board
    form_class = BoardForm
    template_name = 'boards/board_form.html'
    success_url = reverse_lazy('board_list')

    def dispatch(self, request, *args, **kwargs):
        object = self.get_object()
        # 현재 사용자가 게시글을 업데이트할 권한이 있는지 확인
        if object.writer.id != request.session.get('user'):
            messages.error(request, '수정 권한이 없습니다.')
            return redirect('board_list')
        return super().dispatch(request, *args, **kwargs)

# 게시글을 삭제하는 클래스
class BoardDeleteView(DeleteView):
    model = Board
    form_class = BoardForm  
    template_name = 'boards/board_confirm_delete.html'
    success_url = reverse_lazy('board_list')

    def dispatch(self, request, *args, **kwargs):
        object = self.get_object()
        # 현재 사용자가 게시글을 삭제할 권한이 있는지 확인
        if object.writer.id != request.session.get('user'):
            messages.error(request, '삭제 권한이 없습니다.')
            return redirect('board_list')
        return super().dispatch(request, *args, **kwargs)

# 새로운 댓글 작성을 처리하는 클래스
class CommentWriteView(View):
    def post(self, request, board_id):
        form = CommentForm(request.POST)
        if form.is_valid():
            user_id = request.session.get('user')
            user = User.objects.get(pk=user_id)

            # 새로운 댓글 객체를 생성하고 데이터베이스에 저장
            comment = Comment()
            comment.post = get_object_or_404(Board, pk=board_id)
            comment.author = user
            comment.comment = form.cleaned_data['comment']
            parent_id = request.POST.get('parent')
            if parent_id:
                parent_comment = Comment.objects.get(id=parent_id)
                comment.parent = parent_comment
            comment.save()

            return redirect('board_detail', pk=board_id)
        else:
            return HttpResponse(f'Form is not valid: {form.errors}')
