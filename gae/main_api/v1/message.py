from protorpc import messages, message_types


class UserReceive(messages.Message):
  name        = messages.StringField (1, required=True)
  language    = messages.StringField (2, required=True)

class UserSend(messages.Message):
  key         = messages.StringField (1, required=True)
  name        = messages.StringField (2, required=True)
  language    = messages.StringField (3, required=True)

class UserSendCollection(messages.Message):
  items       = messages.MessageField(UserSend, 1, repeated=True)
  pagination  = messages.StringField (2, required=False)

class UserReceiveList(messages.Message):
  key         = messages.StringField (1, required=True)

class UserReceiveListCollection(messages.Message):
  items       = messages.MessageField(UserReceiveList, 1, repeated=True)
  pagination  = messages.StringField (2, required=False)


class ProjectReceiveNew(messages.Message):
  name        = messages.StringField (1, required=True)
  description = messages.StringField (2, default="")
  is_public   = messages.BooleanField(3, default=True)

class ProjectReceiveList(messages.Message):
  pagination  = messages.StringField (1, required=False)

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
  items       = messages.MessageField(ProjectSend, 1, repeated=True)
  pagination  = messages.StringField (2, required=False)


class IssueReceiveNew(messages.Message):
  project       = messages.IntegerField      (1, required=True)
  subject       = messages.StringField       (2, required=True)
  description   = messages.StringField       (3, default="")
  assignee      = messages.StringField       (4, required=False)

class IssueReceiveList(messages.Message):
  project       = messages.IntegerField      (1, required=True)
  pagination    = messages.StringField       (2, required=False)

class IssueReceive(messages.Message):
  key           = messages.StringField       (1, required=True)
  subject       = messages.StringField       (2, required=True)
  description   = messages.StringField       (3, default="")
  assignee      = messages.StringField       (4, required=False)

class IssueReceiveToggle(messages.Message):
  key           = messages.StringField       (1, required=True)

class IssueSend(messages.Message):
  project       = messages.IntegerField      (1, required=True)
  subject       = messages.StringField       (2, required=True)
  description   = messages.StringField       (3, required=True)
  assignee      = messages.StringField       (4, required=False)
  key           = messages.StringField       (5, required=True)
  closed_on     = message_types.DateTimeField(6, required=False)
  will_start_at = message_types.DateTimeField(7, required=True)
  author        = messages.IntegerField      (8, required=True)

class IssueSendCollection(messages.Message):
  items         = messages.MessageField(IssueSend, 1, repeated=True)
  pagination    = messages.StringField       (2, required=False)


class WorkLoadReceive(messages.Message):
  active        = messages.BooleanField      (1, required=False)

class WorkLoadReceiveNew(messages.Message):
  issue         = messages.StringField       (1, required=True)

class WorkLoadReceiveList(messages.Message):
  project       = messages.IntegerField      (1, required=True)
  pagination    = messages.StringField       (2, required=False)

class WorkLoadReceiveClose(messages.Message):
  pass

class WorkLoadSend(messages.Message):
  issue         = messages.StringField       (1, required=True)
  end_at        = message_types.DateTimeField(2, required=False)
  user          = messages.StringField       (3, required=True)
  project       = messages.IntegerField      (4, required=True)
  start_at      = message_types.DateTimeField(5, required=False)
  project_name  = messages.StringField       (6, required=True)
  issue_subject = messages.StringField       (7, required=True)
  user_name     = messages.StringField       (8, required=True)

class WorkLoadSendCollection(messages.Message):
  items         = messages.MessageField(WorkLoadSend, 1, repeated=True)
  pagination    = messages.StringField       (2, required=False)


class CommentReceive(messages.Message):
  issue         = messages.StringField       (1, required=True)
  body          = messages.StringField       (2, required=True)

class CommentReceiveList(messages.Message):
  project       = messages.IntegerField      (1, required=False)
  issue         = messages.StringField       (2, required=False)
  pagination    = messages.StringField       (3, required=False)

class CommentReceiveUpdate(messages.Message):
  body          = messages.StringField       (2, required=True)
  key           = messages.StringField       (3, required=True)

class CommentSend(messages.Message):
  issue         = messages.StringField       (1, required=True)
  body          = messages.StringField       (2, required=True)
  key           = messages.StringField       (3, required=True)
  project       = messages.IntegerField      (4, required=True)
  time_at       = message_types.DateTimeField(5, required=True)
  author        = messages.StringField       (6, required=True)
  author_name   = messages.StringField       (7, required=True)
  update_at     = message_types.DateTimeField(8, required=False)

class CommentSendCollection(messages.Message):
  items         = messages.MessageField(CommentSend, 1, repeated=True)
  pagination    = messages.StringField       (2, required=False)
