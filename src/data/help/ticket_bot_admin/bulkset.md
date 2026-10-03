>>> Sets the ticket value for all users with a specific role.

**Fields**:
`role`: the role of users to set tickets for. Fill via autocomplete.
`tickets`: the number of ticket to set users with the role at. Must be >= 0.
`ignore` (optional): the role of users to ignore when setting tickets. Fill via autocomplete.

**Format**: `/ticketadmin bulkset <role> <tickets> <*optional*:ignore>`

E.g. **/ticketadmin bulkset @mods 2**
This would set all @mods' tickets to 2