tokens = ["1", "2", "+", "3", "*", "4", "-"]

def eval_rpn(tokens):
    stack = []
    for ele in tokens:    
        if ele not in "+-*/":
            stack.append(int(ele))
        else:
            b = stack.pop()
            a = stack.pop()
            if ele == "+":
                stack.append(a + b)
            elif ele == "-":
                stack.append(a - b)
            elif ele == "*":
                stack.append(a * b)
            elif ele == "/":
                stack.append(int(a / b))
    return stack[0]

print(eval_rpn(tokens))
