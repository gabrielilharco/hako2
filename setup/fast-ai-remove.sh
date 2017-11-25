#!/bin/bash
aws ec2 disassociate-address --association-id eipassoc-96bbfea2
aws ec2 release-address --allocation-id eipalloc-aca9c89e
aws ec2 terminate-instances --instance-ids i-0fcfae289cb7ee38b
aws ec2 wait instance-terminated --instance-ids i-0fcfae289cb7ee38b
aws ec2 delete-security-group --group-id sg-16a10f65
aws ec2 disassociate-route-table --association-id rtbassoc-0662447c
aws ec2 delete-route-table --route-table-id rtb-9cb9efe7
aws ec2 detach-internet-gateway --internet-gateway-id igw-70668e09 --vpc-id vpc-01d6c778
aws ec2 delete-internet-gateway --internet-gateway-id igw-70668e09
aws ec2 delete-subnet --subnet-id subnet-70f6c25c
aws ec2 delete-vpc --vpc-id vpc-01d6c778
echo If you want to delete the key-pair, please do it manually.
