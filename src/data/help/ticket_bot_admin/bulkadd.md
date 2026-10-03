>>> Adds tickets to all user with a specific role.

**Fields**:
`role`: the role of users to add tickets to. Fill via autocomplete.
`tickets`: the number of ticket to add to users with the role. Must be >= 0.
`ignore` (optional): the role of users to ignore when adding tickets. Fill via autocomplete.

**Format**: `/ticketadmin bulkadd <role> <tickets> <*optional*:ignore>`

E.g. **/ticketadmin bulkadd @mods 2**
This would add 2 tickets to all @mods