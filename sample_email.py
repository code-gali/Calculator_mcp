def send_mail(subject, body, receivers, cc_receivers, review_date):
    #receivers_list = list(receivers)  # Convert tuple to list
    receivers_list = receivers
    cc_receivers_list = list(cc_receivers)  # Convert tuple to list
    all_recipients = receivers_list + cc_receivers_list  # Combine TO and CC lists
    receivers_str = ', '.join(receivers_list)  # Join the email addresses with commas
    cc_receivers_str = ', '.join(cc_receivers_list)  # Join the CC email addresses with commas
 
    try:
        date = datetime.strptime(review_date, '%m-%d-%Y').date()
        start_hour = 12
        start_minute = 0
        sender = 'noreply-arb-info@elevancehealth.com'
        subject = subject
        description = "Join this meeting for ARB"
        location = "Microsoft Teams Meeting"
        reminder_hours = 15
 
        tz = pytz.timezone("US/Eastern")
        start = tz.localize(dt.datetime.combine(date, dt.time(start_hour, start_minute, 0)))
        end = start + timedelta(hours=1)
 
        # Build the event itself
        cal = Calendar()
        cal.add('prodid', '-//My calendar application//example.com//')
        cal.add('version', '2.0')
        cal.add('method', "REQUEST")
 
        event = Event()
        event.add('organizer', sender)
        event.add('status', "confirmed")
        event.add('category', "Event")
        event.add('summary', subject)
        event.add('description', description)
        event.add('location', location)
        event.add('dtstart', start)
        event.add('dtend', end)
        event.add('dtstamp', datetime.now(pytz.utc))
        event['uid'] = uuid.uuid4()
        event.add('priority', 5)
        event.add('sequence', 1)
        event.add('created', datetime.now(pytz.utc))
 
        # Add a reminder
        alarm = icalendar.Alarm()
        alarm.add("action", "DISPLAY")
        alarm.add('description', "Reminder")
        alarm.add("TRIGGER;RELATED=START", f"-PT{reminder_hours}H")
        event.add_component(alarm)
 
        for receiver in receivers_list:
            attendee = vCalAddress(f'MAILTO:{receiver}')
            attendee.params['cn'] = vText(receiver.split('@')[0])
            attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
            attendee.params['RSVP'] = vText('TRUE')
            event.add('attendee', attendee, encode=0)
 
        for cc_receiver in cc_receivers_list:
            attendee = vCalAddress(f'MAILTO:{cc_receiver}')
            attendee.params['cn'] = vText(cc_receiver.split('@')[0])
            attendee.params['ROLE'] = vText('OPT-PARTICIPANT')
            attendee.params['RSVP'] = vText('TRUE')
            event.add('attendee', attendee, encode=0)
 
        cal.add_component(event)
 
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = sender
        message['To'] = receivers_str
        message['Cc'] = cc_receivers_str
        message["Content-class"] = "urn:content-classes:calendarmessage"
 
        message.attach(MIMEText(body, 'html'))
 
        filename = "invite.ics"
        part = MIMEBase('text', "calendar", method="REQUEST", name=filename)
        part.set_payload(cal.to_ical())
        encoders.encode_base64(part)
        part.add_header('Content-Description', filename)
        part.add_header("Content-class", "urn:content-classes:calendarmessage")
        part.add_header("Filename", filename)
        part.add_header("Path", filename)
        message.attach(part)
 
        smtpObj = get_ser_conn(logger, env=env, region_name=region_nm, aplctn_cd=aplctn_cd, port=None, tls=True, debug=False)
        mail_res = smtpObj.sendmail(sender, all_recipients, message.as_string())
        logger.info("Email sent successfully")
        smtpObj.quit()
        return mail_res
 
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise