# multi-obj-recommender-system
The multi-objective learning recommender system based on machine learning is based on the data of the OnlineJudge system of the School. It will implement self-study and personalized learning for students, and provides adaptive learning with real-time recommendation.

---

+ Method of calculate the $$\theta_i$$ of problems' difficulty parameter is that: $$x_{i}=\frac{1}{N}\sum_{i=1}^{N}y_i $$, $$x_{i}$$ is the $$i_{th}$$ difficulty level of the problem, $y_i$ is every problem's $AC_{ratio}$.
+ Method of calculate the $distance$ between one of users' feature is that: $dis = \frac{1}{N}\sum_{i=1}^{N}\sqrt{x_{i1}^2-x_{i2}^2}$

