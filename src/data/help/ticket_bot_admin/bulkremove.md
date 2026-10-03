>>> Removes tickets from all users with a specific role.

**Fields**:
`role`: the role of users to remove tickets from. Fill via autocomplete.
`tickets`: the number of ticket to remove from users with the role. Must be >= 0.
`ignore` (optional): the role of users to ignore when removing tickets. Fill via autocomplete.

**Format**: `/ticketadmin bulkremove <role> <tickets> <*optional*:ignore>`

E.g. **/ticketadmin bulkremove @mods 2 `ignore:`@bots**
This would remove 2 tickets from all @mods that aren't @bots