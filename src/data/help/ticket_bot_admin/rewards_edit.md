>>> This edits an existing reward.

**Fields**:
`item`: ID of the reward. Found via `/ticket rewards list`.
`name` (optional): reward name.
`cost` (optional): reward cost. Must be >= 0.
`stock` (optional): amount of the reward to sell. Negative values mean `unlimited`.
`pagecolour` (optional): colour of the reward's `inspect` page. Must be a valid hex.
`changedesc` (optional): Set to True to be prompted to change the reward description.

When an optional field is provided, the value will override the existing value on the reward. Non-specified values are left unchanged.

**Format**: `/ticketadmin rewards edit <item> <*optional*:name> <*optional*:cost> <*optional*:stock> <*optional*:pagecolour> <*optional*:changedesc>`

E.g. **/ticketadmin rewards edit 123asd123 `name:`z `changedesc:`True**
Reward `123asd123` would have its name updated to `z`. Its cost, stock, and pagecolour would not be changed. Since `changedesc` = True, a description prompt would appear, which could be used to change the reward image.