# Templates

A template is the frame around every message: the header, the footer, the logo, the colours, the unsubscribe link. Campaigns are rendered inside a campaign template, transactional emails inside a `tx` template. You usually design them in Listmonk's editor, but creating and maintaining them from code is useful when you deploy the same look to several instances or keep your templates in version control.


# The one rule

Every template body must contain the placeholder `{ template "content" . }` exactly where the message goes. Listmonk renders the campaign body or the transactional message into that spot. [`create_template()`](../reference/create_template.md) checks for it and raises `ValueError` before sending anything if it is missing.

``` python
body = '''
<html><body>
  <header><img src="https://example.com/logo.png" alt="Example"></header>
  {{ template "content" . }}
  <footer>[Unsubscribe]({{ UnsubscribeURL }})</footer>
</body></html>
'''
tmpl = listmonk.create_template(name='Brand frame', body=body, type='campaign')
```

Templates use Go's template syntax, so it is `{ .Subscriber.FirstName }` and `{ template "content" . }`, not Jinja's `{% %}` blocks. The [Listmonk templating docs](https://listmonk.app/docs/templating/) list the functions and fields available.


# Campaign templates and transactional templates

Pass `type='campaign'` or `type='tx'`. A campaign template wraps the campaign body. A `tx` template wraps a transactional message and can carry its own subject line:

``` python
reset = listmonk.create_template(
    name='Password reset',
    subject='Your reset code',
    body='<p>Hi {{ .Subscriber.FirstName }}, your code is {{ .Tx.Data.reset_code }}. {{ template "content" . }}</p>',
    type='tx',
)
```

The `tx` template's ID is what you pass to [`send_transactional_email()`](../reference/send_transactional_email.md); a campaign template's ID is what you pass to [`create_campaign()`](../reference/create_campaign.md). They are not interchangeable.


# Reading and previewing

``` python
for tmpl in listmonk.templates():
    print(tmpl.id, tmpl.type, tmpl.name, tmpl.is_default)

tmpl = listmonk.template_by_id(3)          # Template or None
html = listmonk.template_preview_by_id(3).preview
```

[`templates()`](../reference/templates.md) returns both kinds in one request. [`template_preview_by_id()`](../reference/template_preview_by_id.md) renders the template with lorem-ipsum sample content so you can check the frame without sending anything.


# Updating

``` python
tmpl = listmonk.template_by_id(3)
tmpl.body = tmpl.body.replace('2025', '2026')
tmpl = listmonk.update_template(tmpl)
```

[`update_template()`](../reference/update_template.md) sends the name, subject, body, and type and returns the re-fetched template. It does not change the default flag; that is a separate call. Note that the placeholder check runs on create only, so keep `{ template "content" . }` in the body when you edit it, or the server will reject the update.


# The default template

``` python
listmonk.set_default_template(3)   # True, or False if there is no template 3
```

[`set_default_template()`](../reference/set_default_template.md) marks a template as the default for its type. A campaign created with `template_id=None` renders with the default campaign template, so this is how you change the look of every campaign that does not pick one explicitly.


# Deleting

``` python
listmonk.delete_template(3)  # True, or False if it did not exist
```

Listmonk refuses to delete the default template for a type, which comes back as an `httpx2.HTTPStatusError`; make another template the default first.
