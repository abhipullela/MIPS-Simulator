.data
array:  .space 400        # up to 100 integers
temp:   .space 400

.text
.globl main


main:

    # read N
    li   $v0, 5
    syscall
    addu $s0, $v0, $zero            # s0 = N

    li   $t0, 0              # i = 0
    la   $t1, array

read_loop:
    beq  $t0, $s0, input_done

    li   $v0, 5
    syscall

    sll  $t2, $t0, 2
    add  $t3, $t1, $t2
    sw   $v0, 0($t3)

    addi $t0, $t0, 1
    j    read_loop

input_done:

    la   $a0, array
    li   $a1, 0
    addi $a2, $s0, -1
    jal  mergeSort

    # print sorted array
    li   $t0, 0
    la   $t1, array

print_loop:
    beq  $t0, $s0, exit

    sll  $t2, $t0, 2
    add  $t3, $t1, $t2
    lw   $a0, 0($t3)

    li   $v0, 1
    syscall

    # print space
    li   $a0, 32
    li   $v0, 11
    syscall

    addi $t0, $t0, 1
    j    print_loop


exit:
    li   $v0, 10
    syscall


# mergeSort(arr, left, right)
mergeSort:

    addi $sp, $sp, -16
    sw   $ra, 12($sp)
    sw   $a1, 8($sp)
    sw   $a2, 4($sp)
    sw   $s1, 0($sp)

    bge  $a1, $a2, ms_exit

    add  $t0, $a1, $a2
    sra  $t0, $t0, 1
    addu $s1, $t0, $zero

    # left half
    addu $a2, $s1, $zero
    jal  mergeSort

    # right half
    lw   $a1, 8($sp)
    lw   $a2, 4($sp)
    addi $a1, $s1, 1
    jal  mergeSort

    # merge
    lw   $a1, 8($sp)
    lw   $a2, 4($sp)
    addu $a3, $a2, $zero
    addu $a2, $s1, $zero
    jal  merge

ms_exit:
    lw   $ra, 12($sp)
    lw   $a1, 8($sp)
    lw   $a2, 4($sp)
    lw   $s1, 0($sp)
    addi $sp, $sp, 16
    jr   $ra


# merge(arr, left, mid, right)
merge:

    addi $sp, $sp, -8
    sw   $ra, 4($sp)

    addu $t0, $a1, $zero      # i
    addi $t1, $a2, 1   # j
    addu $t2, $a1, $zero      # k

merge_loop:

    bgt  $t0, $a2, copy_right
    bgt  $t1, $a3, copy_left

    sll  $t3, $t0, 2
    add  $t3, $a0, $t3
    lw   $t4, 0($t3)

    sll  $t5, $t1, 2
    add  $t5, $a0, $t5
    lw   $t6, 0($t5)

    slt  $t7, $t4, $t6
    beq  $t7, $zero, take_right

take_left:
    la   $t8, temp
    sll  $t9, $t2, 2
    add  $t8, $t8, $t9
    sw   $t4, 0($t8)

    addi $t0, $t0, 1
    addi $t2, $t2, 1
    j    merge_loop

take_right:
    la   $t8, temp
    sll  $t9, $t2, 2
    add  $t8, $t8, $t9
    sw   $t6, 0($t8)

    addi $t1, $t1, 1
    addi $t2, $t2, 1
    j    merge_loop

copy_left:
    bgt  $t0, $a2, copy_back

    sll  $t3, $t0, 2
    add  $t3, $a0, $t3
    lw   $t4, 0($t3)

    la   $t8, temp
    sll  $t9, $t2, 2
    add  $t8, $t8, $t9
    sw   $t4, 0($t8)

    addi $t0, $t0, 1
    addi $t2, $t2, 1
    j    copy_left

copy_right:
    bgt  $t1, $a3, copy_back

    sll  $t5, $t1, 2
    add  $t5, $a0, $t5
    lw   $t6, 0($t5)

    la   $t8, temp
    sll  $t9, $t2, 2
    add  $t8, $t8, $t9
    sw   $t6, 0($t8)

    addi $t1, $t1, 1
    addi $t2, $t2, 1
    j    copy_right

copy_back:
    addu $t0, $a1, $zero

copy_loop:
    bgt  $t0, $a3, merge_exit

    la   $t8, temp
    sll  $t9, $t0, 2
    add  $t8, $t8, $t9
    lw   $t4, 0($t8)

    sll  $t3, $t0, 2
    add  $t3, $a0, $t3
    sw   $t4, 0($t3)

    addi $t0, $t0, 1
    j    copy_loop

merge_exit:
    lw   $ra, 4($sp)
    addi $sp, $sp, 8
    jr   $ra
