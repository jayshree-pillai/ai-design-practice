"""Exercise 01: OOP: Customer Support Tickets.

"""
from typing import Literal
PRIORITY_ORDER = {"HIGH":10,"MEDIUM":5, "LOW":1}
Status = Literal["open","complete","in_progress"]
class Ticket:
    def __init__(self,ticket_id,customer_name,category,priority):
        if priority not in PRIORITY_ORDER:
            raise ValueError("Priority must be HIGH, MEDIUM OR LOW")
        self.ticket_id = ticket_id
        self.customer_name = customer_name
        self.category = category
        self.priority = priority
        self.status = "open"

class Queue:
    def __init__(self):
        self._tickets:dict[int,Ticket] = {}

    def add_ticket(self,ticket):
        if ticket.ticket_id in self._tickets:
            raise ValueError("Ticket ID already exists")
        self._tickets[ticket.ticket_id] = ticket

    def get_open_tickets(self):
        return [ ticket for ticket in self._tickets.values() if ticket.status == "open"]

    def close_ticket(self,ticket_id):
        if ticket_id not in self._tickets:
            raise ValueError("ticketID doesnt exist")
        self.tickets[ticket_id].status = "complete"

    def get_open_sorted(self):
        open_tickets = self.get_open_tickets()
        def priority_score(ticket:Ticket)->int:
            return PRIORITY_ORDER[ticket.priority]
        return sorted(open_tickets,key=priority_score,reverse=True)

def main():
    queue = Queue()

    ticket1 = Ticket(1,"Jay","Billing","HIGH")
    ticket2 = Ticket(2,"Bob","Login","LOW")
    ticket3 = Ticket(3,"Alice","Billing","MEDIUM")
    queue.add_tickett(ticket1)
    queue.add_tickett(ticket2)
    queue.add_tickett(ticket3)
    for ticket in queue.get_open_tickets():
        print(f"Name is {ticket.name}")         

if __name__ == "__main__":
    main()
