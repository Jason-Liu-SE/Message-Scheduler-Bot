>>> This starts a trade request with another user.

**Fields**:
`target`: The user that you'd like to trade with. Use the autocomplete to fill this.
`action`: The trade action. Either `send` (send tickets to `target`) or `request` (get tickets from `target`).
`tickets`: The number of tickets to trade. Must be > 0.

Once you submit the command, you'll need to `ready`-up for the trade. Once all parties in the trade are `ready`, the trade will proceed. If either user wants to cancel the trade, they may press the `cancel` button. Alternatively, if `5 minutes` passes and the trade isn't completed, it cancels.

**Format**: `/ticket trade start <target> <action> <tickets>`

E.g. **/ticket trade start @user send 5**
This would start a trade with @user, which if accepted by both parties, would transfer `5 tickets` from the `trade initiator` to @user.