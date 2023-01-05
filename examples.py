import asyncio
import random
import time

from circuit_breaker import circuit_breaker


@circuit_breaker(default_result="Circuit breaker is closed", max_retries=5, timeout=3)
def test_circuit_breaker(number: int, need_exception: bool = True):
    if need_exception and random.randint(1, 2) == 2:
        raise BaseException
    return number


@circuit_breaker(default_result=-1, max_retries=1)
async def test_a_circuit_breaker(number: int, need_exception: bool = True):
    if need_exception and random.randint(1, 2) == 2:
        raise BaseException
    await asyncio.sleep(0.0001)
    return number


async def test_a_circuit_breaker_main():
    for i in range(5):
        print(await test_a_circuit_breaker(i))

if __name__ == "__main__":
    print(f"{'*' * 32} ASYNC IMPLEMENTATION {'*' * 32}")
    asyncio.run(test_a_circuit_breaker_main())
    # exit()
    print(f"{'*' * 32} SYNC IMPLEMENTATION {'*' * 32}")
    bound = 15
    for i in range(bound):
        if i == bound // 2:
            time.sleep(5)
            print(test_circuit_breaker(i, need_exception=False))
        else:
            print(test_circuit_breaker(i))
