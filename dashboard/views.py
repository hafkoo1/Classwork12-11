from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tickets.models import Ticket
from accounts.models import User


@login_required
def dashboard(request):
    user = request.user
    context = {}

    if user.role == 'Client':
        # Клієнт бачить історію своїх заявок за статусами
        user_tickets = Ticket.objects.filter(author=user)
        context['open_count'] = user_tickets.exclude(status__in=['Resolved', 'Closed', 'Rejected']).count()
        context['in_progress_count'] = user_tickets.filter(status='In Progress').count()
        context['resolved_count'] = user_tickets.filter(status='Resolved').count()
        context['closed_count'] = user_tickets.filter(status__in=['Closed', 'Rejected']).count()

    elif user.role == 'Agent':
        # Агент бачить свої призначені заявки та кількість вирішених
        assigned_tickets = Ticket.objects.filter(assignee=user)
        context['assigned_count'] = assigned_tickets.exclude(status__in=['Resolved', 'Closed', 'Rejected']).count()
        context['resolved_count'] = assigned_tickets.filter(status='Resolved').count()
        context['new_available_count'] = Ticket.objects.filter(status='New').exclude(author=user).count()

    elif user.role == 'Manager':
        # Менеджер бачить зведену статистику: кількість заявок за статусами та кількість заявок на кожного агента
        all_tickets = Ticket.objects.all()

        status_stats = {}
        for status_val, status_label in Ticket.STATUS_CHOICES:
            status_stats[status_label] = all_tickets.filter(status=status_val).count()

        agents = User.objects.filter(role='Agent')
        agent_stats = []
        for agent in agents:
            agent_stats.append({
                'agent': agent,
                'count': Ticket.objects.filter(assignee=agent).count()
            })

        context['status_stats'] = status_stats
        context['agent_stats'] = agent_stats
        context['total_tickets'] = all_tickets.count()

    return render(request, 'dashboard/dashboard.html', context)