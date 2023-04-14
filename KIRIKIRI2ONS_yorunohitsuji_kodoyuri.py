#!/usr/bin/env python3
from pathlib import Path
import re

# -ONS変数メモ-

# デバッグモード
DEBUG_MODE = 0

# effect管理用変数
effect_startnum = 10
effect_list = []

# effect生成時に使う関数
def effect_edit(t,f):
	global effect_list

	# 「何ミリ秒間」、「どの画像効果で」フェードするかを引数で受け取りeffect_listに記録、
	# エフェクト番号を(effect_startnumからの)連番で発行
	# また、過去に同一の秒数/画像の組み合わせを利用した場合は再度同じエフェクト番号になる
	list_num = 0
	if re.fullmatch(r'[0-9]+', t):#timeが数字のみ＝本処理

		for i, e in enumerate(effect_list,effect_startnum + 1):#1からだと番号が競合する可能性あり
			if (e[0] == t) and (e[1] == f):
				list_num = i

		if not list_num:
			effect_list.append([t, f])
			list_num = len(effect_list) + effect_startnum
	
	else:
		print('ERROR: effect指定ミス')

	return str(list_num)


#吉里吉里の命令文及び変数指定をざっくりpythonの辞書に変換するやつ
def krcmd2krdict(c):
	kr_dict = {}

	for p in re.findall(r'([A-z0-9-_]+?)=("(.*?)"|([^\t\s]+))', c):
		kr_dict[p[0]] = p[2] if p[2] else p[3]

	return kr_dict


# ディレクトリの存在チェック関数
def dir_check(path_list):

	CHK = True
	for p in path_list:
		if not p.exists():
			print('ERROR: "' + str(p) + '" is not found!')
			CHK = False
			
	return CHK


# 文字列置換
def message_replace(txt):
	if (r'[' in txt):
		print('message error:' + txt)

	cnvl = [
		['1', '１'], ['2', '２'], ['3', '３'], ['4', '４'], ['5', '５'], ['6', '６'], ['7', '７'], ['8', '８'], ['9', '９'], ['0', '０'],

		['a', 'ａ'], ['b', 'ｂ'], ['c', 'ｃ'], ['d', 'ｄ'], ['e', 'ｅ'], ['f', 'ｆ'], ['g', 'ｇ'], ['h', 'ｈ'], ['i', 'ｉ'], ['j', 'ｊ'],
		['k', 'ｋ'], ['l', 'ｌ'], ['m', 'ｍ'], ['n', 'ｎ'], ['o', 'ｏ'], ['p', 'ｐ'], ['q', 'ｑ'], ['r', 'ｒ'], ['s', 'ｓ'], ['t', 'ｔ'], 
		['u', 'ｕ'], ['v', 'ｖ'], ['w', 'ｗ'], ['x', 'ｘ'], ['y', 'ｙ'], ['z', 'ｚ'], 

		['A', 'Ａ'], ['B', 'Ｂ'], ['C', 'Ｃ'], ['D', 'Ｄ'], ['E', 'Ｅ'], ['F', 'Ｆ'], ['G', 'Ｇ'], ['H', 'Ｈ'], ['I', 'Ｉ'], ['J', 'Ｊ'], 
		['K', 'Ｋ'], ['L', 'Ｌ'], ['M', 'Ｍ'], ['N', 'Ｎ'], ['O', 'Ｏ'], ['P', 'Ｐ'], ['Q', 'Ｑ'], ['R', 'Ｒ'], ['S', 'Ｓ'], ['T', 'Ｔ'], 
		['U', '∪'], ['V', '∨'], ['W', 'Ｗ'], ['X', 'Ｘ'], ['Y', 'Ｙ'], ['Z', 'Ｚ'], 

		['%', '％'], ['!', '！'], ['?', '？'], [' ', '　'], [':', '：'], [';', '；'], 
	]

	for v in cnvl:
		txt = txt.replace(v[0], v[1])

	return txt


# txt置換→0.txt出力関数
def text_cnv(default, zero_txt, scenario):

	#default.txtを読み込み
	with open(default, encoding='cp932', errors='ignore') as f:
		txt = f.read()
	
	l = [
		(scenario / 'A000.ks'),
		(scenario / 'A001.ks'),
		(scenario / 'A002.ks'),
		(scenario / 'A002_2.ks'),
		(scenario / 'A003.ks'),
		(scenario / 'A004.ks'),
		(scenario / 'A005.ks'),
		(scenario / 'ending.ks'),
	]

	#シナリオファイルを読み込み
	for p in l:
		with open(p, encoding='cp932', errors='ignore') as f:
			fr = f.read()
			fr = re.sub(r'\[ruby\stext\s?=\s?"(.+?)"\](.+?)', r'(\2/\1)', fr)#ルビをons仕様に
			fr = re.sub(r'\@(.+?)\n', r'[\1]\n', fr)# @からの命令も[]同様に処理したいので
			fr = fr.replace(r'[l]', '@')# 文章停止
			fr = fr.replace(r'[ll]', '@\n')# 文章停止+改行
			fr = fr.replace(r'[cm]', '\n\\')# メッセージ表示を一旦消す?
			fr = fr.replace(r'[pcm]', '\n\\\n')# とりあえずcmと同様の実装で
			fr = fr.replace(r'[r]', '　\n')# 一行完全な空白
			fr = re.sub(r'\[(.+?)\]', r'\n[\1]\n', fr)#ここまで来てまだ文中に挟まってる命令は強制改行
			fr = re.sub(r'\@\n*\\', r'\\', fr)#＠￥両方になってるのを消す
	
			#デコード済みtxt一つごとに開始時改行&サブルーチン化
			if DEBUG_MODE:
				txt += '\n;--------------- '+ str(p.name) +' ---------------'
			txt += '\n*SCR_'+ str(p.name).replace('.', '_') +'\n\n'

			for line in fr.splitlines():
				kakko_line = re.search(r'\[(.+?)\]', line)

				#改行は無視
				if re.match('\n', line):
					pass
				
				#元々コメントアウトのやつ目立たせる
				elif re.match(r';', line):
					line = (r';;;;' + line) if DEBUG_MODE else ''
				
				#gotoと間違えそうなやつ
				elif re.match('\*', line): 
					line = (';' + line) if DEBUG_MODE else ''

				#多分セリフとか
				elif not re.match(r'\[', line):
					#半角置換予定
					line = message_replace(line)

				#命令文 - []内
				elif kakko_line:
					d = krcmd2krdict('kr_cmd=' + kakko_line[1])
					kr_cmd = d['kr_cmd']

					if kr_cmd == 'msgc':
						line = '\\'

					elif kr_cmd == 'wait':
						line = ('wait ' + d['time'])

					elif kr_cmd == 'quake':
						line = ('quake 4,' + d['time'])

					elif kr_cmd == 'jump':
						storage = d['storage']
						
						if (storage == 'logo.ks'):
							line = ('mov %500,1:reset')

						else:
							line = ('goto *SCR_'+ str(storage).replace('.', '_'))

					elif kr_cmd == 'background' or kr_cmd == 'ecgbg':
						storage = d['storage']
						time = d['time']
						method = d['method']
						rule = d.get('rule')
						msgc = d.get('msgc')

						effect_num = effect_edit(time, 'fade') if (method == 'crossfade') else effect_edit(time, rule)

						line = ('bg "data\\bgimage\\' + storage + '.png",' + effect_num)

						if (msgc == 'true'):
							line += '\n\\'

					elif kr_cmd == 'fgitrans':
						#methodはcrossfade固定
						#pageはfore固定
						storage = d['storage']
						time = d['time']
						layer = d['layer']# 0 or 1 →20/21で運用しようかと
						pos = d['pos']
						msgc = d.get('msgc')

						effect_num = effect_edit(time, 'fade')

						line = ('tati "data\\fgimage\\' + storage + '.png",' + effect_num + ',2' + layer + ',"' + pos + '"')

						if (msgc == 'true'):
							line += '\n\\'

					elif kr_cmd == 'fgic':
						layer = d['layer']
						line = ('csp 2' + layer + ':print ' + effect_edit('500', 'fade'))

					elif kr_cmd == 'freeimage':
						layer = d['layer']
						line = ('csp 2' + layer + ':print ' + effect_edit('200', 'fade'))

					elif kr_cmd == 'image':
						#本作だとラストの白背景表示のみ
						line = 'bg white,' + effect_edit('1800', 'fade')

					elif kr_cmd == 'clickskip':
						enabled = d['enabled']

						if (enabled == 'true'):
							line = ''
						else:
							line = 'skipoff'

					elif kr_cmd == 'playse':
						storage = d['storage']
						line = 'dwave 1,"data\\sound\\' + storage + '.ogg"'

					elif kr_cmd == 'playbgm':
						storage = d['storage']
						line = 'bgm "data\\bgm\\' + storage + '.ogg"'

					elif kr_cmd == 'stopbgm':
						line = 'bgmstop'

					elif kr_cmd == 'fadeinbgm':
						storage = d['storage']
						time = d['time']

						line = 'bgmfadein ' + time
						line += ':bgm "data\\bgm\\' + storage + '.ogg"'
						line += ':bgmfadein 0'

					elif kr_cmd == 'fadeoutbgm':
						time = d['time']

						line = 'bgmfadeout ' + time
						line += ':stop'
						line += ':bgmfadeout 0'

					#他
					else:
						if DEBUG_MODE:
							#pass
							print(kr_cmd)

						line = (';' + line) if DEBUG_MODE else ''

				#その他 - エラー防止の為コメントアウト(多分ない)
				else:
					line = (';' + line) if DEBUG_MODE else ''
			
				#変換した命令行が空ではない場合
				if line:
					txt += (line + '\n')#入力

	# エフェクト定義用の配列を命令文に&置換
	add0txt_effect = ''
	for i,e in enumerate(effect_list,effect_startnum+1):

		if e[1] == 'fade':
			add0txt_effect +='effect ' + str(i) + ',10,'+e[0]+'\n'

		else:
			add0txt_effect +='effect ' + str(i) + ',18,'+e[0]+',"data\\rule\\'+str(e[1]).replace('"','')+'.png"\n'
	
	#ガ バ ガ バ 修 正 - 自動改行がONSで再現不可なせいで壊滅的な量になってしまった
	txt = txt.replace('@\n　しか', '\\\n　しか')
	txt = txt.replace(r'使っているのだろうか。@', '使っているのだろうか。\\')
	txt = txt.replace(r'が合わさる。@', 'が合わさる。\\')
	txt = txt.replace(r'もなってくる。@', 'もなってくる。\\')
	txt = txt.replace(r'上目遣いに見た。@', '上目遣いに見た。\\')
	txt = txt.replace(r'、横顔。@', '、横顔。\\')
	txt = txt.replace(r'傾ける。@', '傾ける。\\')
	txt = txt.replace(r'と……）@', 'と……）\\')
	txt = txt.replace(r'残して。@', '残して。\\')
	txt = txt.replace(r'のって！」@', 'のって！」\\')
	txt = txt.replace(r'気が戻ってくる。@', '気が戻ってくる。\\')
	txt = txt.replace(r'なりそう……）@', 'なりそう……）\\')
	txt = txt.replace(r'緊張してしまう。@', '緊張してしまう。\\')
	txt = txt.replace(r'思い浮かぶ。@', '思い浮かぶ。\\\n')
	txt = txt.replace(r'配っているらしい。@', '配っているらしい。\\')
	txt = txt.replace(r'情けない。@', '情けない。\\')
	txt = txt.replace(r'気分になってくる。@', '気分になってくる。\\')
	txt = txt.replace(r'いたします」@', 'いたします」\\')
	txt = txt.replace(r'「ぅ……」@', '「ぅ……」\\')
	txt = txt.replace(r'迫った。@', '迫った。\\')
	txt = txt.replace(r'感じている。@', '感じている。\\')
	txt = txt.replace(r'　……あ」@', '　……あ」\\')
	txt = txt.replace(r'火照る。@', '火照る。\\')
	txt = txt.replace(r'差した気がした。@', '差した気がした。\\')
	txt = txt.replace(r'思えなかった。@', '思えなかった。\\')
	txt = txt.replace(r'しよう）@', 'しよう）\\')
	txt = txt.replace(r'ようがない。@', 'ようがない。\\')
	txt = txt.replace(r'やり方で。@', 'やり方で。\\')
	txt = txt.replace(r'なかったのだ。@', 'なかったのだ。\\')
	txt = txt.replace(r'引きつる。@', '引きつる。\\')
	txt = txt.replace(r'まで――。@', 'まで――。\\')
	txt = txt.replace(r'眺めるなんて。@', '眺めるなんて。\\')
	txt = txt.replace(r'頬ずりをした。@', '頬ずりをした。\\')
	txt = txt.replace(r'言わないで」@', '言わないで」\\')
	txt = txt.replace(r'何時……）@', '何時……）\\')
	txt = txt.replace(r'へと持っていく。@', 'へと持っていく。\\')
	txt = txt.replace(r'不機嫌に言う。@', '不機嫌に言う。\\')
	txt = txt.replace(r'何だったんだろうって思う」@', '何だったんだろうって思う」\\')
	txt = txt.replace(r'ことがある。@', 'ことがある。\\')
	txt = txt.replace(r'しないで！」@', 'しないで！」\\')
	txt = txt.replace(r'う気がする。@', 'う気がする。\\')
	txt = txt.replace(r'聞こえているのだろうか。@', '聞こえているのだろうか。\\')
	txt = txt.replace(r'体を離した。@', '体を離した。\\')
	txt = txt.replace(r'吐き捨てるように言う。@', '吐き捨てるように言う。\\')
	txt = txt.replace(r'しれないな……）@', 'しれないな……）\\')
	txt = txt.replace(r'そしたら――」@', 'そしたら――」\\')
	txt = txt.replace(r'「ん……あ……」@', '「ん……あ……」\\')
	txt = txt.replace(r'できたのだった。@', 'できたのだった。\\')
	txt = txt.replace(r'知らないセリも」@', '知らないセリも」\\')
	txt = txt.replace(r'芙紗の頬が熱くなる。@', '芙紗の頬が熱くなる。\\')
	txt = txt.replace(r'ずっと求め続けたい。@', 'ずっと求め続けたい。\\')
	txt = txt.replace('wait 7000\n@', 'wait 7000\n')
	#txt = txt.replace(r'', '')

	txt = txt.replace(r';<<-EFFECT->>', add0txt_effect)

	#出力結果を書き込み
	open(zero_txt, 'w', errors='ignore').write(txt)

	return


def junk_del(delete_list):

	#リスト内のディレクトリパスでfor
	for d in delete_list:

		#ディレクトリパス内のファイル一覧でfor
		for p in d.glob('*'):

			#削除
			p.unlink()
		
		#ディレクトリも削除
		d.rmdir()

	return


# メイン関数
def main(debug):

	#同一階層のパスを変数へ代入
	same_hierarchy = Path.cwd()

	#debug時にtestフォルダに入れないやつ(default.txt等)はこっちを利用
	same_hierarchy_const = same_hierarchy

	if debug:
		#デバッグ時はtestディレクトリ直下
		same_hierarchy = (same_hierarchy / '_test')

	#利用するパスを辞書に入れ一括代入
	PATH_DICT = {
		#先に準備しておくべきファイル一覧
		'bgimage' :(same_hierarchy / 'data' / 'bgimage'),
		'bgm' :(same_hierarchy / 'data' / 'bgm'),
		'fgimage' :(same_hierarchy / 'data' / 'fgimage'),
		'image' :(same_hierarchy / 'data' / 'image'),
		'others' :(same_hierarchy / 'data' / 'others'),
		'rule' :(same_hierarchy / 'data' / 'rule'),
		'scenario' :(same_hierarchy / 'data' / 'scenario'),
		'sound' :(same_hierarchy / 'data' / 'sound'),
		'system' :(same_hierarchy / 'data' / 'system'),
		'video' :(same_hierarchy / 'data' / 'video'),

		'startup_tjs' :(same_hierarchy / 'data' / 'startup.tjs'),

		'default':(same_hierarchy_const / 'default.txt'),
	}

	PATH_DICT2 = {
		#変換後に出力されるファイル一覧
		'0_txt'  :(same_hierarchy / '0.txt'),
	}

	#ディレクトリの存在チェック
	dir_check_result = dir_check(PATH_DICT.values())

	#存在しない場合終了
	if not dir_check_result:
		return

	#txt置換→0.txt出力
	text_cnv(PATH_DICT['default'], PATH_DICT2['0_txt'], PATH_DICT['scenario'])

	#不要データ削除
	if not debug:
		junk_del([
			PATH_DICT['others'],
			PATH_DICT['scenario'],
			PATH_DICT['video'],
		])


main(DEBUG_MODE)