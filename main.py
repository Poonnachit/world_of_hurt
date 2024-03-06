#! /usr/bin/env python3
"""
world_of_hurt_6_group1_20240305.py: Find the shortest way to Pattaya.
"""
import neo4j
import math

def get_compass_direction(*,vector):
    numerator = (vector[1][1] - vector[0][1])
    denominator = (vector[1][0] - vector[0][0])
    if denominator == 0:
        if numerator >= 0:
            angle = 90
        else:
            angle = 270
    elif numerator == 0:
        if denominator >= 0:
            angle = 0
        else:
            angle = 180
    else:
        fraction = (numerator / denominator)
        # get angle in degrees
        fval=math.degrees(math.atan(fraction))
        # magic.... to get rounding right
        angle = int(math.ceil(round(fval,1)))
        # adjust for quadrant if not quadrant I
        if (denominator < 0): # quandrants II & III
            angle += 180
        elif (numerator < 0): # quandrant IV
            angle += 360
    slotno = ((angle-HALF_SLOTSIZE) // SLOTSIZE) # rotate CLOCKWISE half_slotsize
    # that might move 1/2 of the "E" negative, so fix that special case
    if (slotno < 0):
        slotno = 0.0  # fix the special case
    else:
        slotno += 1.0 # remember, rotate CLOCKWISE by 1
    slotno = int(slotno) % POINT_COUNT
    try:
        retval = DIRECTIONS[slotno]
    except IndexError as xcpn:
        print(f"slotno={slotno:d}, angle={angle:f}:{str(xcpn)}")
    return retval

def get_choice(*, msg="Please enter choice: ", choice_data):
    print("\n", "-" * 70)
    max_len = len(choice_data)
    print(f"Total count = {max_len}")
    while True:
        for numb, data in enumerate(choice_data, start=1):
            print(f"{numb}: {data}")
        try:
            choice = int(input(f"{msg}"))
            if choice <= max_len and choice > 0:
                print(f"You choose {choice} is '{choice_data[choice - 1]}'\n")
                return choice_data[choice - 1]
            else:
                raise ValueError("Invalid input")
        except (ValueError, EOFError) as xcpn:
            # print(xcpn)
            print(f"Please enter a valid choice.(between 1-{max_len})")

def run_my_cypher(*, driver, the_cypher):
    """ For Cypher code that does not return anything normally """
    try:
        records, summary, keys = driver.execute_query(the_cypher, database_=DBNAME)
        if summary.notifications is not None:
            badnews=[]
            for item in summary.notifications:
                if item['severity']!='INFORMATION': # ignore
                    badnews.append(item)
            if len(badnews)==0: # hey, no problems we care about
                return EXIT_SUCCESS
            # we have any bad news
            print(the_cypher)
            print("Oh no:")
            for itemno, item in enumerate(badnews,start=1):
                print(itemno,item)
            print("records:",records)
            print("summary.result_available_after:", summary.result_available_after)
            print("summary.summary_notifications:", summary.summary_notifications)
            return EXIT_FAILURE
    except neo4j.exceptions.ClientError as xcpn:
        print(the_cypher)
        print(xcpn)
        return EXIT_FAILURE
    return EXIT_SUCCESS

def run_my_cypher2(*, driver, the_cypher):
    """ For Cypher code that does return something normally """
    try:
        records, summary, keys = driver.execute_query(the_cypher, database_=DBNAME)
        if summary.notifications is not None:
            badnews=[]
            for item in summary.notifications:
                if item['severity']!='INFORMATION': # ignore
                    badnews.append(item)
            if len(badnews)==0: # hey, no problems we care about
                return EXIT_SUCCESS, records, summary, keys
            # we have any bad news
            print(the_cypher)
            print("Oh no:")
            for itemno, item in enumerate(badnews,start=1):
                print(itemno,item)
            print("records:",records)
            print("summary.result_available_after:", summary.result_available_after)
            print("summary.summary_notifications:", summary.summary_notifications)
            return EXIT_FAILURE, None, None, None
    except neo4j.exceptions.ClientError as xcpn:
        print(the_cypher)
        print(xcpn)
        return EXIT_FAILURE, None, None, None
    return EXIT_SUCCESS, records, summary, keys

def setup(*, driver):
    # drop unique constraint on node names, if it exists
    retcode = run_my_cypher(driver=driver, the_cypher=CYPHER_005)
    if retcode == EXIT_FAILURE:
        return retcode
    # drop index on place names, if it exists
    retcode = run_my_cypher(driver=driver, the_cypher=CYPHER_007)
    if retcode == EXIT_FAILURE:
        return retcode
    # delete myGraph from gds, if it exists
    retcode = run_my_cypher(driver=driver, the_cypher=CYPHER_002)
    if retcode == EXIT_FAILURE:
        return retcode
    # delete any existing nodes & edges from neo4j normal database
    retcode = run_my_cypher(driver=driver, the_cypher=CYPHER_000)
    if retcode == EXIT_FAILURE:
        return retcode
    # add constraint that node names are unique
    retcode = run_my_cypher(driver=driver, the_cypher=CYPHER_006)
    if retcode == EXIT_FAILURE:
        return retcode
    # add index on Place names
    retcode = run_my_cypher(driver=driver, the_cypher=CYPHER_008)
    if retcode == EXIT_FAILURE:
        return retcode
    # add my map data (nodes with names, and edges with distances)
    retcode = run_my_cypher(driver=driver, the_cypher=CYPHER_001)
    if retcode == EXIT_FAILURE:
        return retcode
    # MAGIC_CYPHER; apparently older versions of neo4j REQUIRE an index....
    retcode = run_my_cypher(driver=driver, the_cypher=MAGIC_CYPHER)
    if retcode == EXIT_FAILURE:
        return retcode
    # project my nodes & edges to myGraph so gds can use them
    retcode = run_my_cypher(driver=driver, the_cypher=CYPHER_003)
    if retcode == EXIT_FAILURE:
        return retcode
    
def show_nodes(*, driver):
    #print(f"--- Show all nodes ---")
    retcode, records, summary, keys = run_my_cypher2(
        driver=driver, the_cypher=SHOW_DATA)
    if retcode == EXIT_FAILURE:
        return retcode
    # display the results as a text trip plan
    for record in records:
        record_dict = record.data()['n']
        #print(record_dict['name'])
        
def get_nodes(*, driver):
    #print(f"--- Get all nodes ---")
    retcode, records, summary, keys = run_my_cypher2(
        driver=driver, the_cypher=SHOW_DATA)
    if retcode == EXIT_FAILURE:
        return retcode
    nodes = []
    for record in records:
        record_dict = record.data()['n']
        #print(record_dict['name'])
        nodes.append(record_dict['name'])
    return nodes
    
def shortest_Path(*, driver, start, stop):
    if start == stop:
        print("You are already in", start)
        return
    print(f"\n--- Shortest  Path ---")
    # run GDS Dijkstra's Source-Target shortest path algorithm
    # run GDS Dijkstra's Source-Target shortest path algorithm
    # Sadly, we cannot project properties except numbers, so ....
    # while they give us everything about the nodes, we will have to
    # fetch the edge (relationship) properties one-by-one ourselves
    Plan = SHORT_004.format(start=start, stop=stop)
    retcode, records, summary, keys = run_my_cypher2(
        driver=driver, the_cypher=Plan)
    if retcode == EXIT_FAILURE:
        return retcode
    # display the results as a text trip plan
    for record in records:
        record_dict = record.data()
        position_lst = []
        node_has_lights = {} # dictionary with node name key, boolean value
        for x in record_dict['path']:
            position_lst.append(( x["longitude"],x["latitude"],))
            node_has_lights[x['name']]=x['has_lights']

        position_with_next_position = list(zip(position_lst[:-1],position_lst[1:]))

        compass = [get_compass_direction(vector=i) for i in position_with_next_position]

            #print(node_has_lights[x['name']])
            #print(node_has_lights)
        # process nodeNames to determine what edges to query
        bob = list(zip(record_dict['nodeNames'][1:],
                       record_dict['nodeNames'][:-1]))
        """
        [('Bang Saen', 'Bang Prah'), ('Bang Prah', 'Sri Racha'),
         ('Sri Racha', 'Laem Chabang'), ('Laem Chabang', 'Nah Klua'), ('Nah Klua', 'Pattaya')]
        """
        #print(f"\n\nbob = {bob}")
        road_names = [] # list of road names in edge order for our path
        for atuple in bob:
            edge_query = GET_ROAD_NAME.format(myfrom=atuple[0],myto=atuple[1])
            #print(edge_query)
            retcode, records, summary, keys = run_my_cypher2(
                driver=driver, the_cypher=edge_query)
            if retcode == EXIT_FAILURE:
                return retcode
            # if we get here, query ran and we should pull out the data
            temp_dict = records[0].data()
            road_names.append(temp_dict['r.name'])
        print(f"Shortest route from {record_dict['sourceNodeName']:s} to "
              f"{record_dict['targetNodeName']:s} is a "
              f"{record_dict['totalCost']:0.2f} km trip.")
        firsttime=True
        sofar = 0.0
        node_count = len(record_dict['nodeNames'])
        current_node = 0
        current_direction = 0
        for place, distance in zip(record_dict['nodeNames'],record_dict['costs']):
            current_node += 1
            if firsttime:
                firsttime=False
                print(f"Start in {place:s},")
            else:
                print(f"then go {distance-sofar:0.2f} km {compass[current_direction]} "
                      f"on {road_names[current_node-2]:s} to {place:s}", end="")
                if current_node == node_count:
                    print(" and you have arrived at your destination.")
                else:
                    if node_has_lights[place]>0:
                        print(f" and stop at {node_has_lights[place]} light", end="")
                    print(",")
                current_direction += 1
                sofar = distance

def main():
    try:
        with neo4j.GraphDatabase.driver(URI, auth=AUTH) as driver:
            setup(driver=driver)
            #show_nodes(driver=driver)
            nodes = get_nodes(driver=driver)
            start = get_choice(msg="Enter choice for Start: ", choice_data=nodes)
            stop = get_choice(msg="Enter choice for Stop: ", choice_data=nodes)
            shortest_Path(driver=driver, start=start, stop=stop)
            
    except neo4j.exceptions.ServiceUnavailable as xcpn:
        # driver is chatty and shows the message itself
        #print(expn, file=sys.stderr)
        return EXIT_FAILURE
    except KeyboardInterrupt as xcpn:
        print("User Exit Ctrl-C")
        return EXIT_SUCCESS
    return EXIT_SUCCESS

SHOW_DATA = """\
match (n) return n
"""

SHORT_004 = """\
MATCH (source:Place {{name: '{start:s}'}}), (target:Place {{name: '{stop:s}'}})
CALL gds.shortestPath.dijkstra.stream('myGraph', {{
    sourceNode: source,
    targetNode: target,
    relationshipWeightProperty: 'distance'
}})
YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
RETURN
    index,
    gds.util.asNode(sourceNode).name AS sourceNodeName,
    gds.util.asNode(targetNode).name AS targetNodeName,
    totalCost,
    [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS nodeNames,
    costs,
    nodes(path) as path
ORDER BY index;
"""

CYPHER_000 = """\
MATCH (n)
DETACH DELETE n;
"""
CYPHER_001 = """\
CREATE (cbc:Place {name:'Chon Buri City', has_lights: True, lights: 4 , latitude:13.316981353656189, longitude:101.1054655491503}),
       (nm :Place {name:'Nongmon', has_lights: True, lights: 2 , latitude:13.281336054586172 , longitude: 100.93576006686155}),
       (bs:Place {name:'Bang Saen', has_lights: True, lights: 2 , latitude:13.284032758647088, longitude:100.91505482695099}),
       (bp:Place {name:'Bang Prah', has_lights: True, lights: 4 , latitude:13.23791289812828, longitude:101.0053249817564}),
       (sr:Place {name:'Sri Racha', has_lights: True, lights: 4 , latitude:13.16660584434079, longitude:100.93142505997919}),
       (lc:Place {name:'Laem Chabang', has_lights: False, lights: 0 , latitude:13.058630060567513, longitude:100.89192029660816}),
       (nk:Place {name:'Nah Klua', has_lights: True, lights: 3 , latitude:12.951644701190196, longitude:100.89588359259541}),
       (dz:Place {name:'Pattaya', has_lights: True, lights: 4 , latitude:12.927875304270085, longitude:100.87459272561088}),
       (i1:Place {name:'Intersection 1', has_lights: False, lights: 0, latitude:12.922878104715263, longitude:100.88363866368884}),
       (i2:Place {name:'Intersection 2', has_lights: False, lights: 0, latitude:13.002044610980109, longitude:100.93034487653325}),
       
       (cbc)-[:CONNECTS_TO {distance: 15, name: 'Highway 3', lane: 4}]->(nm),
       (bs)-[:CONNECTS_TO {distance: 9, name: 'Kao Lam Road'}]->(i1),
       (i1)-[:CONNECTS_TO {distance: 20, name: 'Blue Motorway 7'}]->(i2),
       (i2)-[:CONNECTS_TO {distance: 11, name: 'White Highway 7'}]->(lc),
       (i2)-[:CONNECTS_TO {distance: 26, name: 'Green Motorway 7'}]->(nk),
       (bs)-[:CONNECTS_TO {distance:9, name: 'Highway 3'}]->(bp),
       (nm)-[:CONNECTS_TO {distance:5, name: 'longhardbangsaen'}]->(bp),
       (nm)-[:CONNECTS_TO {distance:4, name: 'longhardbangsaen'}]->(bs),
       (bp)-[:CONNECTS_TO {distance:6, name: 'Highway 3', lane: 3}]->(sr),
       (sr)-[:CONNECTS_TO {distance:10, name: 'Highway 3', lane: 4}]->(lc),
       (lc)-[:CONNECTS_TO {distance:22, name: 'Highway 3', lane: 4}]->(nk),
       (nk)-[:CONNECTS_TO {distance:1, name: 'Highway 3', lane: 4}]->(dz),
       
       (nm)-[:CONNECTS_TO {distance: 15, name: 'Highway 3', lane: 4}]->(cbc),
       (i1)-[:CONNECTS_TO {distance: 9, name: 'Kao Lam Road'}]->(bs),
       (i2)-[:CONNECTS_TO {distance: 20, name: 'Blue Motorway 7'}]->(i1),
       (lc)-[:CONNECTS_TO {distance: 11, name: 'White Highway 7'}]->(i2),
       (nk)-[:CONNECTS_TO {distance: 26, name: 'Green Motorway 7'}]->(i2),
       (bp)-[:CONNECTS_TO {distance:9, name: 'Highway 3', lane: 4}]->(bs),
       (bp)-[:CONNECTS_TO {distance:5, name: 'longhardbangsaen'}]->(nm),
       (bs)-[:CONNECTS_TO {distance:4, name: 'longhardbangsaen'}]->(nm),
       (sr)-[:CONNECTS_TO {distance:6, name: 'Highway 3', lane: 4}]->(bp),
       (lc)-[:CONNECTS_TO {distance:10, name: 'Highway 3', lane: 4}]->(sr),
       (nk)-[:CONNECTS_TO {distance:22, name: 'Highway 3', lane: 4}]->(lc),
       (dz)-[:CONNECTS_TO {distance:1, name: 'Highway 3', lane: 4}]->(nk);
"""
CYPHER_002 = """\
CALL gds.graph.drop('myGraph', false)
YIELD graphName;
"""
CYPHER_003 = """\
CALL gds.graph.project(
    'myGraph',
    'Place',
    {CONNECTS_TO: {orientation: 'UNDIRECTED'}},
    {
        relationshipProperties: 'distance'
    }
);
"""
# Pattaya Bang Saen
CYPHER_004 = """\
MATCH (source:Place {name: 'Pattaya'}), (target:Place {name: 'Bang Saen'})
CALL gds.shortestPath.dijkstra.stream('myGraph', {
    sourceNode: source,
    targetNode: target,
    relationshipWeightProperty: 'distance'
})
YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
RETURN
    index,
    gds.util.asNode(sourceNode).name AS sourceNodeName,
    gds.util.asNode(targetNode).name AS targetNodeName,
    totalCost,
    [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS nodeNames,
    costs,
    nodes(path) as path
ORDER BY index;
"""
CYPHER_005 = f"""\
DROP CONSTRAINT nodes_are_unique IF EXISTS;
"""
CYPHER_006 = """\
CREATE CONSTRAINT nodes_are_unique IF NOT EXISTS FOR (p:Place) REQUIRE (p.name) IS UNIQUE;
"""
CYPHER_007 = """\
DROP INDEX name_index IF EXISTS;
"""
CYPHER_008 = """\
CREATE INDEX name_index IF NOT EXISTS FOR (p:Place) ON (p.name);
"""
MAGIC_CYPHER = """\
CREATE LOOKUP INDEX node_label_lookup_index IF NOT EXISTS FOR (n) ON EACH labels(n);
"""
GET_ROAD_NAME = """\
MATCH (:Place {{name: '{myfrom:s}'}})-[r:CONNECTS_TO]->(:Place {{name: '{myto:s}'}})
return r.name;
"""
# These globals are for get_compass_direction()
DIRECTIONS = ["East","East North East","North East","North North East","North","North North West","North West","West North West",
                  "West","West South West","South West","South South West","South","South South East","South East","East South East"]
# number of directions (pie slices, points in compass rose)
POINT_COUNT = len(DIRECTIONS)
# map from angle in degrees to direction name
SLOTSIZE = (360 / POINT_COUNT)
HALF_SLOTSIZE = SLOTSIZE / 2 # amount to rotate CLOCKWISE
DBNAME='neo4j'
URI, AUTH = "neo4j://localhost", ("neo4j", "F252545z")
EXIT_SUCCESS, EXIT_FAILURE = 0, 1

if __name__ == '__main__':
    raise SystemExit(main())
