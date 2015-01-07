Embedding widgets
====================

Member
------

If you have a site or a blog that mentions MKs name you need to add 
only one line to your template to get a popup with the latest oknesset data
for all the MKs mentioned ona page. Just before the </body> tag at the bottom
of the template add the line::

    <script type="text/javascript" src="http://oknesset.org/static/js/mk_widget.js"></script>

To see a demo of a page using the Member widget visit https://oknesset.org/static/html/demo-article.html.

To embed a single Knesset member's card, use:

.. code-block:: html

    <iframe width="400" height="186" scrolling="no" style="border:0" src="https://oknesset.org/static/html/mk-iframe.html?id=[member_id]"></iframe>

Replace `member_id` with the id of the member from the url, e.g:


.. code-block:: html

    <iframe width="400" height="186" scrolling="no" style="border:0" src="https://oknesset.org/static/html/mk-iframe.html?id=885"></iframe>

You can get the embedding code for the member's page. For example visit
https://oknesset.org/member/885/, and click the `"עמבד"` button:

.. image:: ../_static/mk_embed.png
