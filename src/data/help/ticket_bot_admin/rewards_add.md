>>> Adds a reward to the rewards listing.

**Fields**:
`name`: reward name.
`cost`: reward cost. Must be >= 0.
`stock` (optional): amount of the reward to sell. Negative values mean `unlimited`. Default=-1.
`pagecolour` (optional): colour of the reward's `inspect` page. Must be a valid hex. Default=FFFFFF.

After the initial `rewards add` command is sent, a followup message is required to set the description. You can attach an image to the reward when editing the description. One image can be attached. If more than one image is attached, the first attached image is taken.

**Format**: `/ticketadmin rewards add <name> <cost> <*optional*:stock> <*optional*:pagecolour>`

E.g. **/ticketadmin rewards add Diamonds 5 4 FFFF00**
This would add a reward with name `Diamonds` for a cost of `5 tickets` with `4` items in stock. Additionally, the colour of the reward's `/ticketadmin rewards inspect` page would be yellow, or `FFFF00` in hex.