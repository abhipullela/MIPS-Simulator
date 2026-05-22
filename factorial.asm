.text
main:
	li $v0, 5
	syscall
	
	addu $t0, $v0, $zero #n
	
	addi $t1, $t1, 1 #f(n)
	loop:
		beq $t0, $zero, ans
		mul $t1, $t0, $t1
		subi $t0, $t0, 1
		j loop
	ans:
		li $v0, 1
		addu $a0, $t1, $zero
		syscall
	
	li $v0, 10
	syscall
