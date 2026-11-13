
from tickets.models import Ticket, Comment


def get_user_tickets(user):
    if user.role == 'Client':
        return Ticket.objects.filter(author=user)

    elif user.role == 'Agent':
        return Ticket.objects.filter(assignee=user) | Ticket.objects.filter(status='New').exclude(author=user)

    elif user.role == 'Manager':
        return Ticket.objects.all()

    return Ticket.objects.none()


def get_ticket_by_id(ticket_id):
    return Ticket.objects.get(id=ticket_id)


def get_ticket_comments(ticket, user):
    comments = Comment.objects.filter(ticket=ticket)

    if user.role == 'Client':
        comments = comments.filter(is_internal=False)

    return comments.order_by('created_at')
