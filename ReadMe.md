设计的不仅仅是简单的agent，是agent的基类
其中包括了:
1. ReAct推理模型，没有action
2. ToolCallAgent 不进行推理，直接action
3. ReAct+ToolCallAgent，推理完了以后进行action

多agent协作就考虑使用autogen的方法
planner会先制定谁和谁可以同时做，谁和谁不能同时做，最终得到一个array
[[agent1, agent2], [agent3], [agent4, agent5]]
然后我有一个公共的聊天区，所有agent都可以从这里得到上一步的结果，然后就按顺序迭代每个子array，对应不同的task
完成了以后，把消息存在公共聊天区，下一个agent执行。
然后这个array，用户可以自己设定，也可以依赖planneragent的生成，planner是通过tool_call来实现这个东西的








