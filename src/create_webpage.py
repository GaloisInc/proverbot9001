from bs4 import BeautifulSoup
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
        # for link in soup.findAll('link'):
        #     link['href'] = link['href'].replace("alectryon.css", "{{url_for('static', filename='alectryon.css')}}")
        #     link['href'] = link['href'].replace("pygments.css", "{{url_for('static', filename='pygments.css')}}")
        # for script in soup.findAll('script'):
        #     script['src'] = script['src'].replace("alectryon.js", "{{url_for('static', filename='alectryon.js')}}")
        for div in soup.find_all("div", {'class':'alectryon-banner'}): 
            div.decompose()
        if (soup.title is not None):
            new_title = soup.new_tag("title")
            new_title.string = "Synthesis Results"
            soup.title.replace_with(new_title)
        # back_button = soup.new_tag("a", href="/", **{"class":"button"})
        # back_button.string = "Go back"
        # soup.head.append(back_button)
        soup.head.append(soup.new_tag("script", src="d3.min.js"))
        soup.head.append(soup.new_tag("link", rel="stylesheet", href="d3-min.css"))
        # soup.head.append(soup.new_tag("link", rel="stylesheet", href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css"))
        # soup.head.append(soup.new_tag("link", rel="stylesheet", href="{{url_for('static', filename='footer.css')}}"))
        soup.body.append(soup.new_tag("script", src="d3-tree.js"))
        # soup.body.insert_before("{% include 'title.html' %}")
        # soup.body.append("{% include 'footer2.html' %}")
        with open("modified_html.html", "w") as fp2:
            fp2.write(soup.prettify())
        fp2.close()
    fp.close()
    webbrowser.open("modified_html.html", new=2)

if __name__ == "__main__":
    main()
