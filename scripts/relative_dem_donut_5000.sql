-- 1) Create your target table (if not already created):
CREATE TABLE IF NOT EXISTS jgg_centroid_relative_dem_5000 (
    sgg_cd        text,
    tot_reg_cd    text,
    above_20_5000 numeric,
    below_20_5000 numeric,
    above_50_5000 numeric,
    below_50_5000 numeric
);

-- 2) PL/pgSQL block to loop over 5-digit prefixes and insert:
DO $$
DECLARE
    r_sgg RECORD;
BEGIN
    -- Loop over each distinct first-5-digits prefix
    FOR r_sgg IN
        SELECT DISTINCT SUBSTRING(tot_reg_cd FROM 1 FOR 5) AS sgg_cd
        FROM jgg_centroid_adjusted_buffered
    LOOP
        RAISE NOTICE 'Processing prefix sgg_cd: %', r_sgg.sgg_cd;


        INSERT INTO jgg_centroid_relative_dem_5000 (
            sgg_cd,
            tot_reg_cd,
            above_20_5000,
            below_20_5000,
            above_50_5000,
            below_50_5000
        )
        WITH
            donut AS (
                -- Buffer "donut" for those rows whose tot_reg_cd starts with this prefix
                SELECT
                    b.tot_reg_cd,
                    ST_Difference(b.geom_5030, b.geom_5000) AS geom
                FROM
                    jgg_centroid_adjusted_buffered b
                WHERE
                    b.tot_reg_cd LIKE r_sgg.sgg_cd || '%'
            ),
            standard_value AS (
                -- "Reference" elevation at centroid
                SELECT
                    pt.tot_reg_cd,
                    ST_Value(r.rast, pt.geom) AS stnd
                FROM
                    dem r
                    JOIN jgg_centroid_adjusted_buffered pt
                       ON ST_Intersects(r.rast, pt.geom)
            ),
            donut_raster AS (
                -- Clip DEM by donut polygon
                SELECT
                    d.tot_reg_cd,
                    ST_Clip(r.rast, d.geom) AS rast
                FROM
                    dem r
                    JOIN donut d
                      ON ST_Intersects(r.rast, d.geom)
            ),
            pixel_polygons AS (
                -- Convert each pixel to a polygon, extracting pixel values
                SELECT
                    dr.tot_reg_cd,
                    (ST_PixelAsPolygons(dr.rast)).val AS rast_value
                FROM
                    donut_raster dr
            ),
            final_stats AS (
                -- Compute statistics relative to "standard_value"
                SELECT
                    p.tot_reg_cd,
                    COUNT(*) FILTER (WHERE p.rast_value - sv.stnd > 20) * 1.0 / COUNT(*) AS above_20_5000,
                    COUNT(*) FILTER (WHERE p.rast_value - sv.stnd < -20) * 1.0 / COUNT(*) AS below_20_5000,
                    COUNT(*) FILTER (WHERE p.rast_value - sv.stnd > 50) * 1.0 / COUNT(*) AS above_50_5000,
                    COUNT(*) FILTER (WHERE p.rast_value - sv.stnd < -50) * 1.0 / COUNT(*) AS below_50_5000
                FROM
                    pixel_polygons p
                    JOIN standard_value sv USING (tot_reg_cd)
                GROUP BY
                    p.tot_reg_cd
            )
        SELECT
            r_sgg.sgg_cd AS sgg_cd,
            fs.tot_reg_cd,
            fs.above_20_5000,
            fs.below_20_5000,
            fs.above_50_5000,
            fs.below_50_5000
        FROM
            final_stats fs
        WHERE
            SUBSTRING(fs.tot_reg_cd FROM 1 FOR 5) = r_sgg.sgg_cd;

    COMMIT;

    END LOOP;
END $$;
