@functions_framework.http
def add_product_images(request: flask.Request):
    if request.method == 'POST':
        # (Same code as before for token and user verification)

        request_data = request.get_json()
        product_id = request_data.get('product_id')
        image_urls = request_data.get('image_urls')

        if not product_id or not image_urls:
            return {'error': 'Required fields: product_id and image_urls'}, 400

        if len(image_urls) < 1 or len(image_urls) > 50:
            return {'error': 'The number of images must be between 1 and 50'}, 400

        connection = db.connect()

        try:
            for img_url in image_urls:
                img_id = str(uuid.uuid4())
                insert_image_query = f"""
                    INSERT INTO product_images (id, product_id, url)
                    VALUES (%s, %s, %s)
                """
                connection.execute(insert_image_query, (img_id, product_id, img_url))

            connection.commit()
            connection.close()

            return {'success': 'Product images added successfully'}, 200

        except Exception as e:
            connection.close()
            return {'error': str(e)}, 500

    else:
        return {'error': 'Invalid request method'}, 405
