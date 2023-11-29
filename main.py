from auto_get_terminal_info_zto import GetModelParameter

s = time.time()
gmp = GetModelParameter(savePath="./phone_info_zto_top.csv", mode=0, browserDriverPath='./chromedriver')
gmp.main(_startPage=3, _endPage=5)
e = time.time()
print(总耗时：e - s)
