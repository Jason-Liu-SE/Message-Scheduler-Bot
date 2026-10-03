>>> This starts a coinflip trade with another user. Each user has a 50% chance to win.

**Fields**:
`target`: the target user to start a coinflip trade with.
`wager`: the number of tickets that the winner should get and the loser should lose. Must be > 0.

**Format**: `/ticket trade coinflip <target> <wager>`

E.g. **/ticket trade coinflip @user 5**
This would start a coinflip trade with @user. If @user won, they would get `5 tickets` and the `trade initiator` would lose `5 ticket`.