# Recommender System Tutorial

---

## 环境安装

+ 本地运行和测试使用`python 3.5+`版本，建议使用`Anaconda`作为该毕业设计的python解释器.

+ 需要提前安装的库有：`csv`, `yaml`, `logging`, `pandas`, `numpy`, `request`, `BeautifulSoup(bs4)`, `matplotlib`, `seaborn`(<strong>需要提升版本</strong>), `pymysql`.

+ 需要安装`mysql`数据库，在执行时需要正常启动. 

  以上库在`Anaconda`上基本都有，可能需要安装一下`pymysql`和更新一下`seaborn`的版本，否则可能会造成一些数据可视化的运行失败.

## 使用说明

+ 只需要把该项目解压并部署到相应的工作目录中即可使用。运行`python main.py`，启动该项目即可.
+ 配置文件在`options\train\config.yml`下，在进行数据库配置和OJ用户配置时，可进行适当修改.
+ 该项目的数据可视化部分，在正常的使用过程中只会产生聚类图，其余绘图方法均用于手动测试使用 。可在`test.py`中实例化这个类（`InfoPlot`），然后调用方法，传递参数进行绘图，具体的参数如何传递在该类下的方法中有说明.
+ 该项目目前还使用爬虫的形式进行数据获取，且由于发给测试者测试，我将切换回了单线程数据获取的版本。数据获取和更新的速率较慢（>= 4h）.
+ 该项目会生成一些中间临时csv数据文件，最后调用推荐方法时，该项目会生成推荐列表文件（`recommendation.csv`），并保存至数据库.