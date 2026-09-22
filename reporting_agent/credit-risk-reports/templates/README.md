Put the branded master deck here (e.g. keybank_master.pptx), set `template: templates/keybank_master.pptx`
in each spec (or leave null to inherit), and set MASTER_TITLE / MASTER_CONTENT in reportkit/style.py
to the layout names in that file. Run `python -c "from pptx import Presentation; print([l.name for l in Presentation('templates/keybank_master.pptx').slide_layouts])"` to list them.
