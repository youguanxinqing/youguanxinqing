all:
	echo "nothing"

.PHONY: sort

sort:
	# pdm run python3 sort_line.py --file=../data/poetry.csv --keys=作者,作品
	# pdm run python3 sort_line.py --file=../data/book.csv --keys=作者,作品
	# pdm run python3 sort_line.py --file=../data/mood.csv --keys=日期
	# pdm run python3 sort_line.py --file=../data/internet.csv --keys=日期
	# pdm run python3 sort_line.py --file=../data/video.csv --keys=作品

	pdm run python3 sort_line.py --file=../data/poetry.csv --keys=author,title_or_date
	pdm run python3 sort_line.py --file=../data/book.csv --keys=author,title_or_date
	pdm run python3 sort_line.py --file=../data/mood.csv --keys=title_or_date
	pdm run python3 sort_line.py --file=../data/internet.csv --keys=title_or_date
	pdm run python3 sort_line.py --file=../data/video.csv --keys=title_or_date
