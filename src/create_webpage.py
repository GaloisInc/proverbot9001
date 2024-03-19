from bs4 import BeautifulSoup
import os
import webbrowser

def main():
    with open("trialZd-json_graph.txt", "r") as json_graph:
        d3_tree = json_graph.read()
    json_graph.close()

    with open("d3-interactive.js", "r") as d3_interact:
        with open("d3-tree.js", "w") as d3_tree_file:
            d3_tree_file.write("var treeData = " + d3_tree + ";")
            d3_tree_file.write(d3_interact.read())
        d3_tree_file.close()
    d3_interact.close()

    with open("proved_theorem.html") as fp:
        soup = BeautifulSoup(fp, "lxml")
        for div in soup.find_all("div", {'class':'alectryon-banner'}): 
            div.decompose()
        if (soup.title is not None):
            new_title = soup.new_tag("title")
            new_title.string = "Synthesis Results"
            soup.title.replace_with(new_title)
        soup.head.append(soup.new_tag("script", src="d3.min.js"))
        soup.head.append(soup.new_tag("link", rel="stylesheet", href="d3-min.css"))
        soup.body.append(soup.new_tag("script", src="d3-tree.js"))
        with open("modified_html.html", "w") as fp2:
            fp2.write(soup.prettify())
        fp2.close()
    fp.close()
    if (os.name == 'posix'):
        filepath = os.getcwd()
        fileuri = 'file:///' + filepath + '/modified_html.html'
        webbrowser.open_new_tab(fileuri)
    else:
        webbrowser.open("modified_html.html", new=2)

if __name__ == "__main__":
    main()
