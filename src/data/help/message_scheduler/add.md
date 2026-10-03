>>> Adds the created message to the schedule. Note that a message must be created before it can be added to the schedule, times are specified in EST/EDT, and you can only schedule posts for the future (e.g. if the time is 5:04, you can't schedule a post for any time prior to or equal to 5:04).**Fields**:
`channel`: channel ID to send post.
`day`: day of post.
`month`: month of post.
`year`: year of post >= current year.
`hour`: hour of post (0-23).
`minute`: minute of post (0-59).**Format**: `/ms add <channel> <day> <month> <year> <hour> <minute>`

E.g. **/ms add 1143322446909407323 30 1 2023 23 59**
This would post the message on January 30, 2023 at 11:59 PM to the channel with ID 1143322446909407323