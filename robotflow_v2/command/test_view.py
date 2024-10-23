from view import Reader,Writer


if __name__ == '__main__':
    writer = Writer("127.0.0.1", 4001)
    reader = Reader("127.0.0.1", 4001)

    # 测试Reader

    reader.get_resource_items_by_id("R207",reader)




    # 测试Writer