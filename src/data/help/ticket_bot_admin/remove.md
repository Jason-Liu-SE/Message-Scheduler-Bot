>>> Removes tickets from a user.

**Fields**:
`user`: a user to remove tickets from. Fill via autocomplete.
`tickets`: the number of tickets to remove from the user. Must be >= 0.

**Format**: `/ticketadmin remove <user> <tickets>`

E.g. **/ticketadmin remove @user 2**
This would remove 2 tickets from @user