
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Ticket
from .forms import TicketForm, CommentForm
from .selectors.ticket_selectors import get_user_tickets, get_ticket_comments
from .services.ticket_services import (
    create_ticket,
    change_status,
    change_priority,
    add_comment,
    take_ticket,
    assign_ticket
)


@login_required
def ticket_list(request):
    tickets = get_user_tickets(request.user)

    status = request.GET.get('status')
    priority = request.GET.get('priority')
    category = request.GET.get('category')
    search = request.GET.get('search')
    sort = request.GET.get('sort')

    if status:
        tickets = tickets.filter(status=status)

    if priority:
        tickets = tickets.filter(priority=priority)

    if category:
        tickets = tickets.filter(category_id=category)

    if search:
        tickets = tickets.filter(title__icontains=search)

    if sort == 'priority':
        tickets = tickets.order_by('-priority')
    else:
        tickets = tickets.order_by('-created_at')

    return render(request, 'tickets/ticket_list.html', {
        'tickets': tickets,
        'categories': Ticket._meta.get_field('category').related_model.objects.all()
    })


@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)

        if form.is_valid():
            try:
                ticket = create_ticket(
                    request.user,
                    form.cleaned_data['title'],
                    form.cleaned_data['description'],
                    form.cleaned_data['category'],
                    form.cleaned_data['priority']
                )

                messages.success(request, 'Заявку успішно створено!')
                return redirect('ticket_detail', ticket_id=ticket.id)

            except ValueError as error:
                messages.error(request, str(error))
    else:
        form = TicketForm()

    return render(request, 'tickets/ticket_create.html', {
        'form': form
    })


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.user.role == 'Client' and ticket.author != request.user:
        messages.error(request, 'У вас немає доступу до цієї заявки.')
        return redirect('ticket_list')

    if request.user.role == 'Agent':
        if ticket.assignee != request.user and ticket.status != 'New':
            messages.error(request, 'У вас немає доступу до цієї заявки.')
            return redirect('ticket_list')

        if ticket.author == request.user:
            messages.error(request, 'Ви не можете обробляти власну заявку.')
            return redirect('ticket_list')

    comments = get_ticket_comments(ticket, request.user)

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            try:
                add_comment(
                    ticket,
                    request.user,
                    form.cleaned_data['text'],
                    request.POST.get('is_internal') == 'on'
                )

                messages.success(request, 'Коментар додано!')
                return redirect('ticket_detail', ticket_id=ticket.id)

            except ValueError as error:
                messages.error(request, str(error))
    else:
        form = CommentForm()

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'comments': comments,
        'form': form
    })


@login_required
def ticket_action(request, ticket_id, action):
    if request.method != 'POST':
        return redirect('ticket_list')

    ticket = get_object_or_404(Ticket, id=ticket_id)

    try:
        if action == 'take':
            take_ticket(ticket, request.user)

        elif action == 'resolve':
            change_status(ticket, 'Resolved', request.user)

        elif action == 'waiting':
            change_status(ticket, 'Waiting', request.user)

        elif action == 'reopen':
            change_status(ticket, 'New', request.user)

        elif action == 'close':
            change_status(ticket, 'Closed', request.user)

        elif action == 'reject':
            change_status(ticket, 'Rejected', request.user)

        elif action == 'in_progress':
            change_status(ticket, 'In Progress', request.user)

        else:
            messages.error(request, 'Невідома дія.')
            return redirect('ticket_detail', ticket_id=ticket.id)

        messages.success(request, 'Статус заявки змінено!')

    except ValueError as error:
        messages.error(request, str(error))

    return redirect('ticket_detail', ticket_id=ticket.id)


@login_required
def ticket_priority(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        try:
            change_priority(
                ticket,
                request.POST.get('priority'),
                request.user
            )
            messages.success(request, 'Пріоритет змінено!')
        except ValueError as error:
            messages.error(request, str(error))

    return redirect('ticket_detail', ticket_id=ticket.id)


@login_required
def ticket_assign(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        from accounts.models import User

        agent = get_object_or_404(
            User,
            id=request.POST.get('agent'),
            role='Agent'
        )

        try:
            assign_ticket(ticket, agent, request.user)
            messages.success(request, 'Агента призначено!')
        except ValueError as error:
            messages.error(request, str(error))

    return redirect('ticket_detail', ticket_id=ticket.id)
