all: bridge_riddle.svg bridge_riddle.png

bridge_riddle.svg: bridge_riddle.dot
	dot -Tsvg $< -o $@

bridge_riddle.png: bridge_riddle.dot
	dot -Tpng $< -o $@

bridge_riddle.dot: bridge_riddle.py
	./$< > $@
