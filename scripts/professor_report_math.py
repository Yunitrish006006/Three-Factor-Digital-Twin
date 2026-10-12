"""Native, offline MathML for the report and explicitly labelled teaching math."""
from html import escape


def row(*parts):
    return '<mrow>'+''.join(parts)+'</mrow>'


def variable(name, subscript=None):
    base='<mi>'+escape(name)+'</mi>'
    if subscript is None:
        return base
    return '<msub>'+base+'<mi mathvariant="normal">'+escape(subscript)+'</mi></msub>'


def operator(symbol):
    return '<mo>'+escape(symbol)+'</mo>'


def number(value):
    return '<mn>'+str(value)+'</mn>'


def parentheses(expression):
    return row(operator('('),expression,operator(')'))


def transpose(expression):
    return '<msup>'+expression+'<mi mathvariant="normal">T</mi></msup>'


def inverse(expression):
    return '<msup>'+expression+row(operator('−'),number(1))+'</msup>'


def fraction(numerator,denominator):
    return '<mfrac>'+numerator+denominator+'</mfrac>'


def square(expression):
    return '<msup>'+expression+number(2)+'</msup>'


def matrix(rows):
    cells=''.join('<mtr>'+''.join('<mtd>'+cell+'</mtd>' for cell in cells)+'</mtr>' for cells in rows)
    return row(operator('['),'<mtable columnspacing="0.7em" rowspacing="0.5em">'+cells+'</mtable>',operator(']'))


def function(name,*arguments):
    return row(variable(name),parentheses(row(*sum(([argument,operator(',')] for argument in arguments[:-1]),[]),arguments[-1])))


def derivative(expression):
    d='<mi mathvariant="normal">d</mi>'
    return '<mfrac>'+row(d,expression)+row(d,variable('t'))+'</mfrac>'


def equation(left,right):
    return row(left,operator('='),right)


def math_block(equations,label,slug):
    formulas=''.join('<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="'+
                     escape(description,quote=True)+'">'+expression+'</math>' for expression,description in equations)
    return ('<div class="math-block" data-equation-group="'+slug+'" tabindex="0" role="region" aria-label="'+
            escape(label,quote=True)+'">'+formulas+'</div>')


def thermal_model():
    h,p,a,inlet=[variable('T',index) for index in ('h','p','a','in')]
    f=variable('f'); hp=row(variable('G','hp'),parentheses(row(h,operator('−'),p)))
    pa=row(parentheses(row(variable('G','p'),operator('+'),variable('k','p'),f)),parentheses(row(p,operator('−'),a)))
    out=row(parentheses(row(variable('G','a'),operator('+'),variable('k','a'),f)),parentheses(row(a,operator('−'),inlet)))
    bypass=row(variable('G','b'),parentheses(row(h,operator('−'),inlet)))
    equations=[
        (equation(row(variable('C','h'),derivative(h)),row(variable('P'),operator('−'),hp,operator('−'),bypass)), '熱源熱容量乘以溫度變化率，等於輸入功率減去源片傳熱與旁路熱流'),
        (equation(row(variable('C','p'),derivative(p)),row(hp,operator('−'),pa)), '金屬片熱容量乘以溫度變化率，等於源片熱流減去片氣熱流'),
        (equation(row(variable('C','a'),derivative(a)),row(pa,operator('−'),out)), '空氣熱容量乘以溫度變化率，等於片氣熱流減去與入口的對流熱流'),
        (equation(row(variable('τ','f'),derivative(f)),row(variable('u'),operator('−'),f)), '風扇時間常數乘以風扇比例變化率，等於命令減去風扇比例'),
    ]
    return math_block(equations,'熱模型四個方程，可左右捲動','thermal')


def extra_path():
    expression=row(variable('G','ha'),parentheses(row(variable('T','h'),operator('−'),variable('T','a'))))
    return math_block([(expression,'熱源到空氣的熱導乘以源氣溫差')],'F 模型新增熱流','extra-path')


def continuous_lqr():
    x,u,e,v,A,B,Q,R,P,K=[variable(name) for name in ('x','u','e','v','A','B','Q','R','P','K')]
    cost=row(transpose(e),Q,e,operator('+'),transpose(v),R,v)
    dt=row('<mi mathvariant="normal">d</mi>',variable('t'))
    integral='<msubsup>'+operator('∫')+number(0)+operator('∞')+'</msubsup>'
    equations=[
        (row(equation(e,row(x,operator('−'),variable('x','eq'))),operator(';'),equation(v,row(u,operator('−'),variable('u','eq')))), '狀態與操作相對平衡點的偏差'),
        (equation(derivative(e),row(A,e,operator('+'),B,v)), '連續偏差狀態方程'),
        (equation(variable('J'),row(integral,parentheses(cost),dt)), '零至無限時間的連續二次成本積分'),
        (row(equation(v,row(operator('−'),K,e)),operator(';'),equation(K,row(inverse(R),transpose(B),P))), '連續狀態回授與增益'),
        (equation(row(transpose(A),P,operator('+'),P,A,operator('−'),P,B,inverse(R),transpose(B),P,operator('+'),Q),number(0)), '連續代數 Riccati 方程'),
    ]
    return math_block(equations,'連續 LQR 教學公式，可左右捲動','continuous-lqr')


def discrete_lqr():
    x,u,e,v,Q,R,P,K=[variable(name) for name in ('x','u','e','v','Q','R','P','K')]
    A,B=variable('A','d'),variable('B','d')
    def sample(expression,next_step=False):
        return row(expression,operator('['),variable('k'),operator('+')+number(1) if next_step else '',operator(']'))
    matrix=inverse(parentheses(row(R,operator('+'),transpose(B),P,B)))
    estimated='<mover accent="true">'+e+operator('^')+'</mover>'
    summation='<munderover>'+operator('∑')+equation(variable('k'),number(0))+operator('∞')+'</munderover>'
    equations=[
        (row(equation(e,row(x,operator('−'),variable('x','eq'))),operator(';'),equation(v,row(u,operator('−'),variable('u','eq')))), '狀態與操作偏差定義'),
        (equation(sample(e,True),row(A,sample(e),operator('+'),B,sample(v))), '離散偏差狀態方程'),
        (equation(variable('J'),row(summation,parentheses(row(transpose(sample(e)),Q,sample(e),operator('+'),transpose(sample(v)),R,sample(v))))), '零至無限步的離散二次成本總和'),
        (equation(P,row(transpose(A),P,A,operator('−'),transpose(A),P,B,matrix,transpose(B),P,A,operator('+'),Q)), '離散代數 Riccati 方程'),
        (equation(K,row(matrix,transpose(B),P,A)), '離散 LQR 增益'),
        (equation(sample(u),row(variable('u','eq'),operator('−'),K,sample(estimated))), '實務命令等於平衡命令減去增益乘以估測偏差'),
    ]
    return math_block(equations,'離散 LQR 教學公式，可左右捲動','discrete-lqr')


def workpoint():
    F=variable('F'); x,u,d=[variable(n,'eq') for n in ('x','u','d')]
    e,v,A,B,E=[variable(n) for n in ('e','v','A','B','E')]
    def jac(w):
        return row(fraction(row(operator('∂'),F),row(operator('∂'),variable(w))),operator('|'),variable('eq'))
    eqs=[(equation(function('F',x,u,d),number(0)),'非線性模型在平衡點等於零'),
         (row(derivative(e),operator('≈'),A,e,operator('+'),B,v,operator('+'),E,variable('δ'),variable('d')),'局部模型含狀態偏差、操作偏差與擾動偏差'),
         (row(equation(A,jac('x')),operator(';'),equation(B,jac('u')),operator(';'),equation(E,jac('d'))),'工作點的三個 Jacobian')]
    return math_block(eqs,'平衡點與線性化','workpoint')


def thermal_jacobian():
    Ghp,Gb,g,h,kp,ka=[variable(n,s) for n,s in [('G','hp'),('G','b'),('g',None),('h',None),('k','p'),('k','a')]]
    Ch,Cp,Ca,tau=[variable(n,s) for n,s in [('C','h'),('C','p'),('C','a'),('τ','f')]]
    Dp,Da=variable('Δ','pa'),variable('Δ','ai')
    z=number(0); neg=lambda x:row(operator('−'),x)
    A=matrix([[neg(fraction(row(Ghp,operator('+'),Gb),Ch)),fraction(Ghp,Ch),z,z],
              [fraction(Ghp,Cp),neg(fraction(row(Ghp,operator('+'),g),Cp)),fraction(g,Cp),neg(fraction(row(kp,Dp),Cp))],
              [z,fraction(g,Ca),neg(fraction(row(g,operator('+'),h),Ca)),fraction(row(kp,Dp,operator('−'),ka,Da),Ca)],
              [z,z,z,neg(fraction(number(1),tau))]])
    eqs=[(equation(variable('A'),A),'四狀態熱模型的連續 Jacobian 矩陣'),
         (equation(variable('B'),transpose(matrix([[z,z,z,fraction(number(1),tau)]]))),'風扇命令只直接進入風扇動態'),
         (equation(variable('C'),matrix([[z,number(1),z,z],[z,z,number(1),z]])),'只有金屬片和空氣溫度的量測矩陣')]
    return math_block(eqs,'四狀態矩陣，可左右捲動','thermal-jacobian')


def zoh():
    A,B=variable('A'),variable('B'); dt=variable('Δt'); tau=variable('τ')
    exponential=lambda x:row('<mi mathvariant="normal">exp</mi>',parentheses(x))
    integral='<msubsup>'+operator('∫')+number(0)+dt+'</msubsup>'
    eqs=[(equation(variable('A','d'),exponential(row(A,dt))),'零階保持的狀態轉移矩陣'),
         (equation(variable('B','d'),row(integral,exponential(row(A,tau)),B,'<mi mathvariant="normal">d</mi>',tau)),'零階保持的輸入矩陣積分')]
    return math_block(eqs,'零階保持離散化','zoh')


def hjb():
    e,v,P,A,B,Q,R,K=[variable(n) for n in ('e','v','P','A','B','Q','R','K')]
    future=equation(function('V',e),row(transpose(e),P,e))
    minimum='<munder><mi mathvariant="normal">min</mi>'+v+'</munder>'
    h=equation(number(0),row(minimum,parentheses(row(transpose(e),Q,e,operator('+'),transpose(v),R,v,operator('+'),number(2),transpose(e),P,parentheses(row(A,e,operator('+'),B,v))))))
    stationarity=equation(row(number(2),R,v,operator('+'),number(2),transpose(B),P,e),number(0))
    eqs=[(future,'二次形式的最優未來成本'),(h,'定常 Hamilton Jacobi Bellman 方程'),
         (stationarity,'對操作求導為零'),
         (equation(v,row(operator('−'),inverse(R),transpose(B),P,e)),'得到負狀態回授'),
         (equation(derivative(function('V',e)),row(operator('−'),transpose(e),parentheses(row(Q,operator('+'),transpose(K),R,K)),e)),'理想最優軌跡上成本函數的變化率')]
    return math_block(eqs,'連續 LQR 推導與 Lyapunov 主線','hjb')


def bellman():
    e,v,P,Q,R=[variable(n) for n in ('e','v','P','Q','R')]
    A,B=variable('A','d'),variable('B','d')
    future=parentheses(row(A,e,operator('+'),B,v))
    minimum='<munder><mi mathvariant="normal">min</mi>'+v+'</munder>'
    eqs=[(equation(function('V',e),row(minimum,parentheses(row(transpose(e),Q,e,operator('+'),transpose(v),R,v,operator('+'),transpose(future),P,future)))),'Bellman 的當步成本加未來成本'),
         (equation(row(parentheses(row(R,operator('+'),transpose(B),P,B)),v,operator('+'),transpose(B),P,A,e),number(0)),'展開後對操作求導，除以二')]
    return math_block(eqs,'離散 Bellman 推導，可左右捲動','bellman')


def scalar_example():
    P,K,a,b,q,r=[variable(n) for n in ('P','K','a','b','q','r')]
    eqs=[(equation(row(number('0.0004'),square(P),operator('+'),number('0.00356'),P,operator('−'),number('0.1')),number(0)),'一維 DARE 化成二次方程'),
         (row(P,operator('≈'),number('11.975666'),operator(';'),K,operator('≈'),number('−2.239932')),'選取正根的成本與回授增益'),
         (row(a,operator('−'),b,K,operator('≈'),number('0.935201')),'理想閉迴路特徵值'),
         (row(variable('u'),operator('≈'),number(40),operator('+'),number('4.479864'),operator('='),number('44.479864'),operator('%')),'偏差二度時，提高約四點四八個 PWM 百分點')]
    return math_block(eqs,'自選一維數學例題；不是機箱實測','scalar-example')


def normalization():
    x,v,Q,R=[variable(n) for n in ('e','v','Q','R')]
    S,T=variable('S'),variable('T')
    eqs=[(row(equation(variable('ẽ'),row(inverse(S),x)),operator(';'),equation(variable('ṽ'),row(inverse(T),v))),'依允許偏差尺度正規化'),
         (row(equation(Q,row(transpose(parentheses(inverse(S))),variable('W','x'),inverse(S))),operator(';'),equation(R,row(transpose(parentheses(inverse(T))),variable('W','u'),inverse(T)))),'由無量綱權重回到物理量權重')]
    return math_block(eqs,'成本權重與單位換算','normalization')


TEACHING_EQUATIONS={
    'workpoint':workpoint,'thermal-jacobian':thermal_jacobian,'zoh':zoh,
    'continuous-lqr':continuous_lqr,'hjb':hjb,'discrete-lqr':discrete_lqr,
    'bellman':bellman,'scalar-example':scalar_example,'normalization':normalization,
}
