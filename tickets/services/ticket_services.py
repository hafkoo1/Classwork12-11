from django.utils import timezone
from tickets.models import Ticket, Comment


def create_ticket(user, title, description, category, priority):
    if user.role != 'Client':
        raise ValueError('Лише клієнт може створювати заявки.')

    open_tickets = Ticket.objects.filter(
        author=user
    ).exclude(status__in=['Resolved', 'Closed', 'Rejected']).count()

    if open_tickets >= 5:
        raise ValueError('Можна мати не більше 5 відкритих заявок.')

    ticket = Ticket.objects.create(
        title=title,
        description=description,
        category=category,
        priority=priority,
        author=user
    )

    return ticket


def take_ticket(ticket, agent):
    if agent.role != 'Agent':
        raise ValueError('Лише агент може взяти заявку.')

    if ticket.author == agent:
        raise ValueError('Не можна обробляти власну заявку.')

    if ticket.assignee and ticket.assignee != agent:
        raise ValueError('Заявка вже призначена іншому агенту.')

    if ticket.status != 'New':
        raise ValueError('Ця заявка вже не є новою.')

    ticket.assignee = agent
    ticket.status = 'In Progress'
    ticket.save()

    return ticket


def assign_ticket(ticket, agent, manager):
    if manager.role != 'Manager':
        raise ValueError('Лише менеджер може призначати агентів.')

    if agent.role != 'Agent':
        raise ValueError('Виконавцем може бути лише агент.')

    if ticket.is_closed:
        raise ValueError('Не можна призначити закриту заявку.')

    if ticket.author == agent:
        raise ValueError('Агент не може обробляти власну заявку.')

    ticket.assignee = agent
    ticket.save()

    return ticket


def change_status(ticket, new_status, user):
    if ticket.is_closed:
        raise ValueError('Заявка вже закрита або відхилена.')

    allowed_transitions = {
        'New': ['In Progress', 'Rejected'],
        'In Progress': ['Waiting', 'Resolved', 'Rejected'],
        'Waiting': ['In Progress', 'Resolved', 'Rejected'],
        'Resolved': ['Closed'],
    }

    if user.role == 'Client':
        if ticket.author != user:
            raise ValueError('Це не ваша заявка.')

        if new_status == 'New' and ticket.can_reopen:
            ticket.status = 'New'
            ticket.resolved_at = None
            ticket.save()
            return ticket

        if new_status == 'Closed' and ticket.status == 'Resolved':
            ticket.status = 'Closed'
            ticket.save()
            return ticket

        raise ValueError('Клієнту не дозволено змінювати цей статус.')

    elif user.role == 'Agent':
        if ticket.assignee != user:
            raise ValueError('Ця заявка вам не призначена.')

        if ticket.author == user:
            raise ValueError('Не можна обробляти власну заявку.')

    elif user.role != 'Manager':
        raise ValueError('Недостатньо прав.')

    if new_status not in allowed_transitions.get(ticket.status, []):
        raise ValueError('Недопустимий перехід статусу.')

    ticket.status = new_status

    if new_status == 'Resolved':
        ticket.resolved_at = timezone.now()

    ticket.save()

    return ticket


def change_priority(ticket, priority, user):
    if user.role != 'Manager':
        raise ValueError('Змінювати пріоритет може лише менеджер.')

    ticket.priority = priority
    ticket.save()

    return ticket


def add_comment(ticket, user, text, is_internal=False):
    if ticket.is_closed:
        raise ValueError('Не можна коментувати закриту заявку.')

    if user.role == 'Client':
        if ticket.author != user:
            raise ValueError('Це не ваша заявка.')

        if is_internal:
            raise ValueError('Клієнт не може залишати внутрішні коментарі.')

    elif user.role == 'Agent':
        if ticket.author == user:
            raise ValueError('Не можна коментувати власну заявку.')
        # Агент може коментувати, якщо вона призначена йому АБО якщо це нова заявка у системі
        if ticket.status != 'New' and ticket.assignee != user:
            raise ValueError('Ви не можете коментувати цю заявку.')

    elif user.role != 'Manager':
        raise ValueError('Недостатньо прав.')

    comment = Comment.objects.create(
        ticket=ticket,
        author=user,
        text=text,
        is_internal=is_internal
    )

    return comment