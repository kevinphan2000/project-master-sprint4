family void main(){
   DESTRUCTION x = 5;
   foo(foo(x));
}

family DESTRUCTION foo(DESTRUCTION x){
    takeMyMoney(x);
}
# this should pass