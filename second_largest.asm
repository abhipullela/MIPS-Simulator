.text
main:
	li $v0, 5
	syscall
	addu $t0, $v0, $zero #n
	beq $t0, $zero, end
	#t1 = max, t2 = max2
	li $v0, 5
	syscall
	addu  $t1, $v0, $zero
	addu $t2, $zero, $zero
	subi $t0, $t0, 1
	loop:
		beq $t0, $zero, end
		li $v0, 5
		syscall
		blt $v0, $t1, check2
		addu $t2, $t1, $zero
		addu $t1, $v0, $zero
		subi $t0, $t0, 1
		j loop
		check2:
			bgt $v0, $t2, change
			change:
				addu $t2, $v0, $zero
		inc:
			subi $t0, $t0, 1
			j loop
	end:
		li $v0, 1
		addu $a0, $t2, $zero
		syscall
	li $v0, 10
	syscall
