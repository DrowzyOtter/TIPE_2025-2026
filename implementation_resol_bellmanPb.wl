"""CreateDocument[Plot[Sin[x],{x,0,2 Pi}]]"""
"""Export["plot_sin.png", Plot[Sin[x],{x,0,2 Pi}]]"""

"""H = x'[t]2 + y'[t]2 + λ[t] * (x[t] * Cos[t] + y[t] * Sin[t] - 1);"""

H = Sqrt[x'[t]^2 + y'[t]^2] + \[Lambda][t] * (x[t] * Cos[t] + y[t] * Sin[t] - 1); 
Needs["VariationalMethods`"]; 
EulerEquations[H, {x[t], y[t], \[Lambda][t]}, t]; 
(D[D[H, x'[t]], t] - D[H, x[t]]) * Sin[t] - (D[D[H, y'[t]], t] - D[H, y[t]]) * Cos[t] /. {x'[t] -> D[(1 - Sin[t]) y[t], t]/Cos[t], x''[t] -> D[(1 - Sin[t]) y[t], {t, 2}]/Cos[t]} // Simplify; 
pts = 102; 
aa = N@Range[0, 2\[Pi], 2\[Pi] / (pts - 1)]; 
grid = Flatten[Outer[List, aa, aa], 1];

Export["MonGraphiqueGrid.png", ListPlot[grid,Joined -> True]]