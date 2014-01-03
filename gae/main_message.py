from protorpc import messages

class UserSend(messages.Message):
  user_id     = messages.StringField (1, required=True)
  name        = messages.StringField (2, required=True)

class UserReceive(messages.Message):
  name        = messages.StringField (1, required=True)

class UserSendCollection(messages.Message):
  items = messages.MessageField(UserSend, 1, repeated=True)

class ProjectSend(messages.Message):
  name        = messages.StringField (1, required=True)
  description = messages.StringField (2, required=True)
  is_public   = messages.BooleanField(3, required=True)
  closed      = messages.BooleanField(4, required=True)
  archive     = messages.BooleanField(5, required=True)
  admin       = messages.StringField (6, repeated=True)
  member      = messages.StringField (7, repeated=True)

class ProjectReceive(messages.Message):
  name        = messages.StringField (1, required=True)
  description = messages.StringField (2, required=True)

class ProjectSendCollection(messages.Message):
  items = messages.MessageField(ProjectSend, 1, repeated=True)
