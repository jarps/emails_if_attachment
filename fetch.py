import imaplib
import email

imapserver = "imap.gmail.com"
emuser     = "your_email_addr"
empw       = "your_email_pw"
inbox      = "inbox"    

def init():
    mail = imaplib.IMAP4_SSL(imapserver)
    mail.login(emuser, empw)
    mail.select(inbox)
    uids = mail.uid('search', None, "ALL")[1][0].split()
    #comment above line and uncomment below to search a range of emails by UID:
    #highly recommended for inboxes > 500 emails. ex. below is for emails with UID 12500-most recent
    #uids = mail.uid('search', '(UID 12500:*)', "ALL")[1][0].split()
    return [mail, uids]

#could modify to accept daterange
def emaildict(idlist, mailobj):
    vals = dict()
    for i, v in enumerate(idlist):
        # RFC822 is the body of the email, BODYSTRUCTURE is the structure of the email that you can extract filenames from
        data   = mailobj.uid('fetch', v, '(RFC822 BODYSTRUCTURE)')[1]
        meta   = dict()                 #holds the data we wish to associate with the email's UID
        struct = data[1].split()        #split bodystructure
        list   = []                     #holds list of attachment filenames

        for j, k in enumerate(struct):
            if k == '("FILENAME"':
                count = 1
                val = struct[j + count]
                while val[-3] != '"':
                    count += 1
                    val += " " + struct[j + count]
                list.append(val[1:-3])
            elif k == '"FILENAME"':
                count = 1
                val = struct[j + count]
                while val[-1] != '"':
                    count += 1
                    val += " " + struct[j + count]
                list.append(val[1:-1])
        if list:
            #has attachments, extract email info and add to result
            raw = email.message_from_string(data[0][1])
            arr = raw['From'].split()
            ##MAYBE: GET BODY TEXT
            meta['email_id'] = v
            meta['subj']  = raw['Subject']
            meta['addr']  = arr[-1]
            meta['attachments'] = list
            print(meta)
            vals[v] = meta
    return vals

def main():
    ini = init()
    mail, uids = ini[0], ini[1]
    try:
        vals = emaildict(uids, mail)
        #print(vals)
        mail.logout()
    except Exception as e:
        print(str(e))
        mail.logout()

if __name__ == '__main__':
    main()
