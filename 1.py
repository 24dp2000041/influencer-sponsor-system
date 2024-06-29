from jonja2 import Template

name= "koooooooooooooi" 
email="|aewtqwtw@gmail.com"

Filr= open("index.html", "r")
content=File.read().
file.close()

template=Template(content)
rendred_form=Template.render(pl_name=name , pl_email=email )
output=open("index.html",'w')
output.write(rendered_form)
output.close()