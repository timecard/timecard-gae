from protorpc import messages, message_types


class UserReceive(messages.Message):
  name        = messages.StringField (1, required=True)
  language    = messages.StringField (2, required=True)

class UserSend(messages.Message):
  user_id     = messages.StringField (1, required=True)
  name        = messages.StringField (2, required=True)
  language    = messages.StringField (3, required=True)

class UserSendCollection(messages.Message):
  items = messages.MessageField(UserSend, 1, repeated=True)


class ProjectReceiveNew(messages.Message):
  name        = messages.StringField (1, required=True)
  description = messages.StringField (2, default="")
  is_public   = messages.BooleanField(3, default=True)

class ProjectReceive(messages.Message):
  key         = messages.IntegerField(1, required=True)
  name        = messages.StringField (2, required=True)
  description = messages.StringField (3, default="")
  is_public   = messages.BooleanField(4, default=True)

class ProjectSend(messages.Message):
  key         = messages.IntegerField(1, required=True)
  name        = messages.StringField (2, required=True)
  description = messages.StringField (3, required=True)
  is_public   = messages.BooleanField(4, required=True)
  closed      = messages.BooleanField(5, required=True)
  archive     = messages.BooleanField(6, required=True)
  admin       = messages.StringField (7, repeated=True)
  member      = messages.StringField (8, repeated=True)

class ProjectSendCollection(messages.Message):
  items = messages.MessageField(ProjectSend, 1, repeated=True)


class IssueReceiveNew(messages.Message):
  project       = messages.StringField       (1, required=True)
  subject       = messages.StringField       (2, required=True)
  description   = messages.StringField       (3, default="")
  assignee      = messages.StringField       (4, required=False)

class IssueReceive(messages.Message):
  subject       = messages.StringField       (2, required=True)
  description   = messages.StringField       (3, default="")
  assignee      = messages.StringField       (4, required=False)
  closed_on     = message_types.DateTimeField(5, required=False)
  key           = messages.IntegerField      (6, required=True)

class IssueSend(messages.Message):
  project       = messages.StringField       (1, required=True)
  subject       = messages.StringField       (2, required=True)
  description   = messages.StringField       (3, required=True)
  assignee      = messages.StringField       (4, required=False)
  key           = messages.IntegerField      (5, required=True)
  closed_on     = message_types.DateTimeField(6, required=False)
  will_start_at = message_types.DateTimeField(7, required=True)
  author        = messages.StringField       (8, required=True)

class IssueSendCollection(messages.Message):
  items = messages.MessageField(IssueSend, 1, repeated=True)
