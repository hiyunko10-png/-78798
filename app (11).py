"""다시, 한 사람 — 독자적인 인생 선택 시뮬레이션.
GitHub: app.py와 requirements.txt를 같은 폴더에 업로드.
Streamlit Community Cloud 진입 파일: app.py
로컬: pip install -r requirements.txt && streamlit run app.py
모든 출생/소득/수명 확률은 게임용 가정이며 실제 국가 통계가 아닙니다.
외부 API/데이터 수집 없음. 세션 저장과 JSON 내보내기 제공.
"""
import streamlit as st
import random, secrets, json, copy, html
from datetime import date
st.set_page_config(page_title='다시, 한 사람',page_icon='🌱',layout='wide')
COUNTRIES=['대한민국','인도','브라질','나이지리아','프랑스','일본','이집트','인도네시아','캐나다','베트남','멕시코','케냐']
NAMES=['이안','서우','민','아리','루','노아','엘리','하루','미카','솔','레오','린']
FOCUS={'균형 잡힌 일상':(1,1,1,1),'배움과 호기심':(-1,0,5,-1),'일과 저축':(-2,-1,1,-1),'사람들과 시간':(0,3,0,5),'건강과 휴식':(5,2,0,0),'창작과 도전':(-1,4,3,0)}
EVENTS={
5:('작은 용기','놀이터에서 혼자 앉아 있는 아이가 보인다. 네 손에는 마지막 사탕 한 알이 있다.',[('사탕을 나누고 이름을 묻는다',{'r':10,'h':5,'friend':True},'그날의 친구는 오래도록 네 생일을 기억했다.'),('옆에 앉아 함께 구름을 본다',{'r':6,'k':4,'friend':True},'둘은 말없이도 함께 있을 수 있다는 걸 배웠다.'),('집에 돌아가 그림으로 남긴다',{'k':9,'h':3},'네 그림 속 두 사람은 나란히 서 있었다.')]),
12:('배움의 갈림길','선생님은 더 깊이 공부해보자고 한다. 집에서는 당장 도울 손이 필요하다.',[('장학 프로그램에 도전한다',{'k':12,'b':-300,'study':True},'서류를 쓰며 처음으로 먼 미래를 상상했다.'),('가족을 돕고 저녁에 공부한다',{'k':6,'r':9,'health':-3,'b':400},'낮과 밤이 서로 다른 교실이 되었다.'),('손으로 만드는 일을 배운다',{'k':7,'b':200,'craft':True},'처음 만든 작은 의자는 조금 흔들렸지만 네 것이었다.')]),
18:('세상으로 가는 문','앞으로 몇 년을 어디에 쓸 것인가. 다른 길이 닫히는 것은 아니지만, 모든 길을 동시에 걸을 수는 없다.',[('대학에 진학한다',{'k':16,'b':-5000,'degree':True},'등록금과 기대가 함께 쌓였다.'),('기술을 배우며 일을 시작한다',{'k':9,'b':1800,'craft':True,'job':'기술직'},'첫 월급보다 네 이름이 적힌 작업복이 더 선명했다.'),('작은 창작 프로젝트를 시작한다',{'h':10,'k':6,'b':-1200,'artist':True,'job':'창작자'},'아무도 주문하지 않은 첫 작품을 세상에 내놓았다.')]),
25:('우연의 이름','비를 피하던 작은 가게에서, 너와 같은 책을 읽는 사람을 만난다.',[('다시 만날 약속을 한다',{'r':14,'h':10,'partner':True},'둘은 같은 페이지에서 서로 다른 문장을 좋아했다.'),('친구로 천천히 알아간다',{'r':10,'h':5,'friend':True},'이름을 저장하고, 다음 비를 기다렸다.'),('혼자만의 시간을 지킨다',{'h':7,'k':4},'혼자라는 말이 외롭다는 말과 같지는 않았다.')]),
32:('값을 매길 수 없는 것','안정적인 일자리 제안과 오래 품었던 계획이 같은 주에 찾아온다.',[('안정을 택하고 주변을 돌본다',{'b':7000,'r':5,'job':'사무직'},'생활에 여백이 생겼다. 모험은 조금 미뤄두었다.'),('독립해서 작은 사업을 연다',{'b':-4000,'h':8,'business':True,'job':'자영업'},'가게 문을 여는 소리는 매일 조금씩 달랐다.'),('공부를 이어가 전문직에 도전한다',{'b':-3500,'k':12,'health':-3,'professional':True},'책상 위 불빛이 다시 밤을 밝혔다.')]),
40:('가족이라는 모양','누군가를 돌볼 수 있을까. 지금 네 삶에 그 자리가 있는지 스스로 묻는다.',[('아이를 키우는 삶을 선택한다',{'child':True,'r':12,'b':-3500,'h':6},'가족이 되는 방식은 서류보다 훨씬 많은 날들로 이루어졌다.'),('가까운 이들의 든든한 이웃이 된다',{'r':12,'h':7,'mercy':True,'b':-500},'네 집에는 언제나 여분의 컵이 있었다.'),('나만의 생활을 단단히 가꾼다',{'health':7,'h':7,'b':1000},'잘 돌본 하루들이 삶을 받쳤다.')]),
50:('몸이 보내는 편지','검진 결과가 도착했다. 당장 위급하지는 않지만 생활을 바꿀 필요가 있다.',[('일을 줄이고 치료와 운동에 집중한다',{'health':17,'b':-3000,'h':4},'예전보다 느린 걸음으로 더 많은 것을 보았다.'),('생활 습관부터 조금씩 바꾼다',{'health':9,'b':-500},'작은 변화는 눈에 잘 띄지 않아도 쌓였다.'),('바쁜 일이 끝난 뒤로 미룬다',{'health':-11,'b':2000},'달력에는 늘 다음 달이 있었다.')]),
60:('돌려주는 시간','오래 쌓아온 경험을 누군가 필요로 한다.',[('후배에게 일을 가르친다',{'r':10,'k':4,'legacy':True},'네가 했던 실수를 누군가는 피할 수 있게 되었다.'),('새로운 취미를 배운다',{'h':13,'k':5,'b':-500},'초보자라는 이름이 오랜만에 즐거웠다.'),('계속 일하며 저축한다',{'b':4000,'health':-4},'익숙한 자리에서 낯익은 계절을 보냈다.')]),
70:('먼 길의 초대','오래전 알고 지내던 사람에게서 편지가 왔다. “아직 늦지 않았다면 한번 만나자.”',[('먼 길을 떠난다',{'h':14,'r':8,'b':-1500,'health':-2},'만나지 못한 세월보다 지금의 한 시간이 소중했다.'),('집으로 초대한다',{'r':12,'h':9,'b':-200},'오래된 이야기는 따뜻한 식탁에서 다시 시작되었다.'),('긴 답장을 써 보낸다',{'h':7,'k':5,'legacy':True},'네 글씨에 세월이 묻어 있었다.')]),
80:('남기고 싶은 문장','너의 삶을 한 문장으로 적어달라는 부탁을 받는다.',[('“사람을 놓치지 않으려 했다.”',{'r':10,'h':5,'legacy':True},'이름 몇 개가 문장 뒤에 조용히 떠올랐다.'),('“모르는 것을 계속 배우고 싶었다.”',{'k':9,'h':5,'legacy':True},'아직 읽지 못한 책들이 기다리고 있었다.'),('“완벽하지 않아도 내 삶이었다.”',{'h':12,'legacy':True},'덜 아픈 후회와 조금 더 선명한 기쁨이 남았다.')])}

def new_life(year,seed=None):
 seed=seed if seed is not None else secrets.randbelow(2**31);r=random.Random(seed)
 s=dict(version=2,seed=seed,name=r.choice(NAMES),country=r.choice(COUNTRIES),year=year,age=0,health=r.randint(65,88),h=r.randint(50,75),k=r.randint(35,65),r=r.randint(40,75),b=r.randint(-300,2000),family=r.choice(['빠듯한','소박한','넉넉한']),job='아직 없음',flags=[],logs=[],done=[],pending=None,alive=True,focus='균형 잡힌 일상',lifespan=r.randint(72,96),memo='',ending=None)
 s['logs']=[{'age':0,'text':f"{s['country']}의 {s['family']} 가정에서 태어났다. 이름은 {s['name']}."}];return s

def clamp(s):
 for k in ['health','h','k','r']:s[k]=max(0,min(100,s[k]))

def log(s,text):s['logs'].append({'age':s['age'],'text':text})
def ending(s):
 if s['r']>=75:return '사람들의 기억 속에','네가 남긴 것은 곁에 머물렀던 시간이었다.'
 if s['k']>=80:return '끝없는 호기심','마지막까지 네 세상에는 새로운 질문이 있었다.'
 if s['b']>100000:return '쌓아 올린 날들','한 번에 만들어진 것은 없었다. 수많은 하루가 지금의 삶을 만들었다.'
 if s['h']>=70:return '작은 기쁨의 수집가','큰 사건보다 작은 순간들이 너의 삶을 빛냈다.'
 return '단 하나의 삶','쉬운 삶은 아니었다. 그래도 너는 여기에 있었고, 누군가는 너를 기억한다.'

def advance(s,n=1):
 if not s['alive'] or s['pending'] is not None:return
 for _ in range(n):
  s['age']+=1;a=s['age'];r=random.Random(s['seed']+a*7919);health,h,k,rel=FOCUS[s['focus']]
  s['health']+=health*.35-(.65 if a>55 else .15);s['h']+=h*.35+r.uniform(-2,1);s['k']+=k*.45;s['r']+=rel*.35+r.uniform(-1,1)
  if 20<=a<66:
   if s['job']=='아직 없음':s['job']='전문직' if 'degree' in s['flags'] else '서비스직'
   annual={'전문직':9000,'기술직':6500,'창작자':4300,'자영업':5500,'사무직':6500,'서비스직':4000}.get(s['job'],4000)
   s['b']+=round(annual*(1.3 if s['focus']=='일과 저축' else 1)*r.uniform(.65,1.2)-3500-(900 if 'child' in s['flags'] else 0))
  elif a>=66:
   s['job']='은퇴';s['b']-=r.randint(100,900)
  if s['b']<0:s['h']-=.5
  clamp(s)
  if a in EVENTS and a not in s['done']:s['pending']=a;log(s,EVENTS[a][0]+' — 선택을 기다리는 중');break
  if a>=s['lifespan']+(4 if s['health']>70 else 0) or s['health']<=0:
   s['alive']=False;s['ending']=ending(s)[0];log(s,'삶의 마지막 장에 도착했다.');break
  if r.random()<.23:
   events=[('좋아하는 노래를 발견했다.',{'h':3}),('예상하지 못한 수리비를 썼다.',{'b':-350}),('누군가에게 고맙다는 말을 들었다.',{'r':3}),('어려운 것을 하나 배웠다.',{'k':2}),('오래 걷고 푹 잠들었다.',{'health':2})]
   text,e=r.choice(events)
   for key,v in e.items():s[key]+=v
   clamp(s);log(s,text)
  elif a%5==0:log(s,'크고 작은 일들 사이로 또 한 계절을 건넜다.')

def decide(s,index):
 a=s['pending']
 if a is None:return
 _,_,options=EVENTS[a];label,effect,result=options[index]
 for key,value in effect.items():
  if key in ['health','h','k','r','b']:s[key]+=value
  elif key=='job':s['job']=value
  elif value and key not in s['flags']:s['flags'].append(key)
 if effect.get('professional'):
  if s['k']>=65:s['job']='전문직';result+=' 오랜 준비 끝에 자격을 얻었다.'
  else:result+=' 아직 준비가 부족했다. 배움은 끝나지 않았다.'
 clamp(s);s['done'].append(a);s['pending']=None;log(s,label+' · '+result)

def validate(s):
 if not isinstance(s,dict) or set(s)!=set(new_life(2026,1)):raise ValueError('저장 항목이 다릅니다.')
 if type(s['version']) is not int or s['version']!=2:raise ValueError('저장 버전 오류')
 for key in ['seed','year','age','lifespan']:
  if type(s[key]) is not int:raise ValueError('숫자 형식 오류')
 if not 0<=s['seed']<2**31 or not 0<=s['age']<=120 or not 1900<=s['year']<=2200 or not 72<=s['lifespan']<=96:raise ValueError('범위 오류')
 for key in ['health','h','k','r','b']:
  if type(s[key]) not in [int,float] or not -10**9<=s[key]<=10**9:raise ValueError('상태 오류')
 for key in ['health','h','k','r']:
  if not 0<=s[key]<=100:raise ValueError('상태 범위 오류')
 if type(s['alive']) is not bool or s['focus'] not in FOCUS or s['country'] not in COUNTRIES:raise ValueError('게임 상태 오류')
 for key in ['name','family','job','memo']:
  if not isinstance(s[key],str) or len(s[key])>2000:raise ValueError('문자열 오류')
 if s['ending'] is not None and not isinstance(s['ending'],str):raise ValueError('결말 오류')
 for key in ['flags','done','logs']:
  if not isinstance(s[key],list) or len(s[key])>1000:raise ValueError('목록 오류')
 if any(not isinstance(v,str) or len(v)>50 for v in s['flags']):raise ValueError('표식 오류')
 if any(type(v) is not int or v not in EVENTS for v in s['done']):raise ValueError('선택 기록 오류')
 if s['pending'] is not None and (type(s['pending']) is not int or s['pending'] not in EVENTS or s['pending']!=s['age']):raise ValueError('대기 선택 오류')
 for e in s['logs']:
  if not isinstance(e,dict) or set(e)!=set(['age','text']) or type(e['age']) is not int or not isinstance(e['text'],str) or len(e['text'])>4000:raise ValueError('연대기 오류')
 return s

st.markdown("""<style>
.stApp{background:#f5f2ea;color:#293b36} .block-container{max-width:1150px;padding-top:2rem} [data-testid="stSidebar"]{background:#ece8dc}h1,h2,h3{font-family:Georgia,'Nanum Myeongjo',serif!important;letter-spacing:-.04em;color:#263e34}.hero{padding:45px 12px 35px;border-bottom:1px solid #d5d9ce}.eyebrow{font-size:12px;color:#566e61;letter-spacing:3px}.hero h1{font-size:clamp(42px,7vw,78px);line-height:1.12;margin:20px 0}.hero p{color:#526456;line-height:1.9;max-width:620px}.card{padding:22px;border:1px solid #ccd3c4;background:#fbfaf5;border-radius:15px;margin:12px 0;line-height:1.8}.age{font:70px Georgia,serif;color:#40634c}.entry{padding:14px 4px;border-bottom:1px solid #d9ddcf;line-height:1.8}.year{font-size:12px;color:#596f60}.stButton>button,.stDownloadButton>button{border-radius:24px;border:1px solid #829a7d;min-height:45px;color:#293b36;background:#fcfaf4} .stButton>button:hover{background:#e1ead9;border-color:#47694f}.quiet{font-size:13px;color:#526456;line-height:1.8}
</style>""",unsafe_allow_html=True)
if 'life' not in st.session_state:st.session_state.life=None
if 'archive' not in st.session_state:st.session_state.archive=[]
if 'archived_seed' not in st.session_state:st.session_state.archived_seed=[]
s=st.session_state.life
with st.sidebar:
 st.subheader('🌱 다시, 한 사람')
 st.caption('시작은 우연, 그다음은 당신의 선택')
 st.info('게임용 가상 모델입니다. 출생 확률·소득·수명은 실제 국가 통계가 아닙니다. 예측이나 의학·재정 조언이 아닙니다.')
 tab=st.radio('둘러보기',['지금의 삶','삶의 책장','저장과 불러오기'])
 if s:
  st.download_button('현재 삶 저장',json.dumps(s,ensure_ascii=False,indent=2,allow_nan=False),'one_life.json','application/json')
  with st.expander('새 삶 시작'):
   confirm=st.checkbox('저장하지 않은 현재 진행은 사라집니다')
   if st.button('시작 화면으로',disabled=not confirm):st.session_state.life=None;st.rerun()
 st.caption('진행·책장은 현재 접속 세션에만 남습니다. 장기 보관은 저장 파일을 이용하세요.')
if tab=='저장과 불러오기':
 st.header('삶을 간직하는 방법');st.write('JSON 저장 파일로 다른 접속에서도 이어갈 수 있습니다. 실제 사람의 개인정보를 입력하지 마세요.')
 f=st.file_uploader('저장 파일',type=['json'])
 if st.button('이 삶 이어가기',disabled=f is None):
  try:
   if f.size>500000:raise ValueError('파일이 너무 큽니다.')
   st.session_state.life=validate(json.loads(f.getvalue()));st.success('불러왔습니다. 왼쪽에서 지금의 삶을 선택하세요.')
  except (ValueError,TypeError,KeyError) as e:st.error(str(e))
 st.stop()
if tab=='삶의 책장':
 st.header('살아낸 삶의 책장');st.caption('현재 접속에서 끝까지 살아낸 삶들입니다. 가상의 이용자나 실시간 접속자 수는 표시하지 않습니다.')
 for item in reversed(st.session_state.archive):
  st.markdown(f"### {item['name']} · {item['age']}세")
  st.write(item['country']+' · '+item['ending']);st.write(item['memo'] or '남긴 한마디가 없습니다.')
 if not st.session_state.archive:st.info('아직 책장에 남겨진 삶이 없습니다.')
 st.stop()
if s is None:
 st.markdown('<section class="hero"><div class="eyebrow">AN INTERACTIVE LIFE STORY</div><h1>다시,<br>한 사람.</h1><p>다른 곳, 다른 가정에서 시작한다면 어떤 삶을 살게 될까요?<br>선택하지 못한 시작과, 스스로 고르는 순간들 사이를 걸어보세요.</p></section>',unsafe_allow_html=True)
 left,right=st.columns([1.5,1],gap='large')
 with left:
  st.subheader('삶의 문을 열기')
  year=st.select_slider('이야기의 시작 연도',options=[1980,1990,2000,2010,2020,2026,2040],value=2026)
  st.caption('연도는 이야기의 달력에만 반영됩니다. 역사 사건·미래 통계 모델은 적용되지 않습니다.')
  st.write('나라·이름·가정 형편은 무작위입니다. 모든 나라는 같은 확률이며 현실의 출생 분포를 재현하지 않습니다.')
  if st.button('새로운 삶으로 태어나기 →',type='primary',use_container_width=True):st.session_state.life=new_life(year);st.rerun()
 with right:
  st.markdown('<div class="card"><b>우연으로 시작해 선택으로 이어지는 이야기</b><br><br>열 번의 중요한 갈림길<br>배움 · 일 · 사랑 · 돌봄 · 노년<br>매년 바꾸는 삶의 초점<br>당신의 선택을 담는 연대기</div>',unsafe_allow_html=True)
 st.caption('가족·경제적 어려움·건강·자연스러운 죽음이 등장합니다. 폭력 묘사는 없습니다. 특정 사이트의 브랜드·문구·데이터를 사용하지 않은 독자적 프로토타입입니다.')
 st.stop()
left,right=st.columns([2,1],gap='large')
with left:
 st.caption(f"{s['year']+s['age']}년 · {s['country']} · {s['family']} 가정에서 시작한 삶")
 st.title(s['name']+'의 한 번뿐인 날들')
 st.markdown(f'<div class="age">{s["age"]}<span style="font-size:22px"> 세</span></div>',unsafe_allow_html=True)
 if s['alive']:
  if s['pending'] is not None:
   title,body,opts=EVENTS[s['pending']];st.subheader(title);st.write(body)
   for i,(label,_,_) in enumerate(opts):
    if st.button(label,key=f'choice_{s["pending"]}_{i}',use_container_width=True):decide(s,i);st.rerun()
   st.caption('선택할 때까지 시간은 흐르지 않습니다.')
  else:
   s['focus']=st.selectbox('올해, 무엇에 마음을 둘까요?',list(FOCUS),index=list(FOCUS).index(s['focus']))
   a,b=st.columns(2)
   if a.button('한 해 살아가기 →',use_container_width=True):advance(s);st.rerun()
   if b.button('다음 5년 살아보기',use_container_width=True):advance(s,5);st.rerun()
   st.caption('5년 진행도 중요한 선택 앞에서는 멈춥니다. 실시간 자동 진행은 하지 않습니다.')
 else:
  title,body=ending(s);st.subheader(title);st.write(body)
  st.write(f"{s['year']} — {s['year']+s['age']} · {s['age']}년의 이야기")
  s['memo']=st.text_area('이 삶에게 남기는 한마디',value=s['memo'],max_chars=500)
  if st.button('이 삶을 책장에 간직하기',disabled=s['seed'] in st.session_state.archived_seed):
   st.session_state.archive.append(copy.deepcopy(s));st.session_state.archived_seed.append(s['seed']);st.success('현재 접속의 책장에 남겼습니다. 영구 보관하려면 왼쪽에서 저장하세요.')
 st.subheader('살아온 날들의 결')
 for e in reversed(s['logs'][-25:]):
  st.markdown(f'<div class="entry"><div class="year">{s["year"]+e["age"]} · {e["age"]}세</div>{html.escape(e["text"])}</div>',unsafe_allow_html=True)
 with st.expander('전체 연대기'):
  for e in s['logs']:st.write(f"{e['age']}세 — {e['text']}")
with right:
 st.subheader('지금의 나')
 for key,label in [('health','건강'),('h','마음의 여유'),('k','배움'),('r','사람들과의 유대')]:st.progress(round(s[key])/100,text=f'{label} · {round(s[key])}')
 st.metric('가상 자산',f"{s['b']:,.0f} 코인")
 st.caption('게임 내 추상 화폐입니다. 실제 통화·구매력과 연결되지 않습니다.')
 st.write('하는 일 · '+s['job'])
 st.write('곁의 사람들')
 for flag,label in [('friend','오래된 친구'),('partner','함께하는 동반자'),('child','돌보는 아이')]:
  if flag in s['flags']:st.write('🌿 '+label)
 st.markdown('<div class="card"><b>삶에는 정답이 없어요.</b><br>높은 숫자만이 좋은 삶을 의미하지 않습니다. 누구와 무엇을 위해 시간을 썼는지도 돌아보세요.</div>',unsafe_allow_html=True)
 st.caption('점수와 사건은 단순화된 가상 규칙입니다. 국적에 따른 능력 차이는 적용하지 않습니다.')
