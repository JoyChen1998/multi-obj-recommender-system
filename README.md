# multi-obj-recommender-system
The multi-objective learning recommender system based on machine learning is based on the data of the OnlineJudge system of the School. It will implement self-study and personalized learning for students, and provides adaptive learning with real-time recommendation. (**use LaTeX to read all functions**)

---

+ Method of calculate the $$\theta_i$$ of problems' difficulty parameter is that: $$\theta_{i}=\frac{1}{N}\sum_{i=1}^{N}y_i $$, $$\theta_{i}$$ is the $$i_{th}$$ difficulty level of the problem, $y_i$ is every problem's $AC_{ratio}$.
+ Method of calculate the $distance$ between one of users' feature is that: $dis(x,y) = \sqrt{\sum_{i=1}^{K}（x_{i}^2-y_{i}^2）}$. ($K$= the number of features )
+ Method of calculate the $factor$ of user's ability is that:
  1. Get the $p_i=count(Problem_{i})$, $i$ => contest problem ($A$ ~ $J$)
  2. Taking $p_6$ as the standard, divide the number of other questions by $p_6$ to get the ratio$(r_i)$. => $$(r_{i}=\frac{p_6}{p_i})$$
  3.  Get user's solution count$$(solved_{i},i\in(Problem))$$ of every level problems.
  4. Get the factor of user's ability. => $$factor=\sum_{i=1}^{10}r_{i}*solved_{i}$$.
+ How to clustering ?
  1. Load all user info.
  2. Calculate user's ability factor.
  3. Use k-means algorithm $$(k=10)$$ to clustering users.
  4. save result as $csv$.

