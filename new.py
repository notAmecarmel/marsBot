num = True
it = 0
resp = "bot response"
while num is True:
    ui = input("input: ")
    it = it + 1
    if it == 3:
        print("email de")
        mail = input("mail: ")
        print("thanks, ", mail, "now name...")
        name = input("name: ")
        print("name is ", name, "mail is ", mail)
        confirm = input("yes or no: ")
        if confirm == "yes":
            pass
    else:
        print("bot: ", resp)