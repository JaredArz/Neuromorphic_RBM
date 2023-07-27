import numpy as np
import data as d
import matplotlib.pyplot as plt

energys = np.asarray(d.e)
avg = list(np.average(energys,axis=0))

final_sols = []
for elem in d.s:
    final_sols.append(elem[25])
correct = 0
for s in final_sols:
    if (s == 28) or (s == 21):
        correct+=1
    else:
        pass
accuracy_percent = (correct/len(final_sols))*100
print(f"percent accuracy is {accuracy_percent}%")

index = 4
sols_sample = d.s[index]
sample = energys[index,:]

Jsot_max    = 5e11      #
Jsot_min    = 1e11      #
Jsot_steps = 26
x = np.linspace(Jsot_min,Jsot_max,Jsot_steps)
# =======================
fig, ax1 = plt.subplots()
ax1.plot(x,sols_sample,color="#3976af")
ax1.axhline(y=sols_sample[25], color="black", linestyle="--",alpha=0.15)

ax2 = ax1.twinx()
ax2.plot(x,sample,alpha=0.5,color="#ef8536")
ax2.axhline(y=sample[25], color="black", linestyle="--",alpha=0.15)
#plt.plot(x,avg)
ax1.set_ylim(-15,69)
ax2.set_ylim(-0.00144,0.00025)
ax1.set_xlabel('Current Density A/m³')
ax1.set_ylabel('Solution in Decimal')
ax2.set_ylabel('System Energy')
fig.tight_layout()
plt.savefig("energy_plotX.png",format="svg")
plt.show()
