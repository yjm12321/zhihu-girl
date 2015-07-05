from zhihu import User

import Queue
import urllib2
import sys
import os
import platform

def main():

    initial_user_url = "http://www.zhihu.com/people/BigMing"
    
    url_queue=Queue.Queue()
    url_queue.put(initial_user_url)

    save_pic_dir0=sys.path[0]+"/pic_female/"
    save_pic_dir1=sys.path[0]+"/pic_male/"
    save_pic_dir2=sys.path[0]+"/pic_emale/"

    saved_count_female=0
    saved_count_male=0
    saved_count_emale=0
    visited_url_count=0
    tried_url_count=0

    IO_error_count=0
    
    limit_count=1000000000
    count=0
    
    flag=True
    
    least_follower=1000
     
    
    while(flag):
        
        if url_queue.qsize()>0:
            current_url=url_queue.get()
            user = User(current_url)

            try:
                print current_url,
                print "     queue_size: ",
                print url_queue.qsize(),
                print "     Saved_size: ",
                print saved_count_male+saved_count_female
                followees = user.get_followees_with_condition(least_follower)
                
                for followee in followees:
                    
                    tried_url_count+=1
                    print "tried_url_count: " + str(tried_url_count)
                    
                    visited_url_count+=1
                    print "visited_url_count: " + str(visited_url_count)
                                       
                    url_queue.put(followee.user_url)

                    try:
                        req = urllib2.Request(followee.user_pic_url) 
                        res = urllib2.urlopen(followee.user_pic_url,timeout=10)
                        pic = res.read()
                        pextention = os.path.splitext(followee.user_pic_url)
                    
                        if platform.system() == 'Windows':
                            pname = followee.user_id.decode('utf-8','ignore').encode('gbk','ignore')
                        else:
                            pname=followee.user_id
                                
                        followee_count=followee.user_followers_num

                        if followee.user_gender==0:
                            p_full_path=save_pic_dir0+str(saved_count_female+1)+"_"+pname+"_"+str(followee_count)+pextention[1]
                            saved_count_female+=1
                                
                        if followee.user_gender==1 :
                            p_full_path=save_pic_dir1+str(saved_count_male+1)+"_"+pname+"_"+str(followee_count)+pextention[1]
                            saved_count_male+=1

                        if followee.user_gender==2 :
                            p_full_path=save_pic_dir2+str(saved_count_emale+1)+"_"+pname+"_"+str(followee_count)+pextention[1]
                            saved_count_emale+=1
                                
                        if followee.user_gender==3 :
                                
                            if followee.get_user_gender()==0:
                                p_full_path=save_pic_dir0+str(saved_count_female+1)+"_"+pname+"_"+str(followee_count)+pextention[1]
                                saved_count_female+=1
                                    
                            if followee.get_user_gender()==1:
                                p_full_path=save_pic_dir1+str(saved_count_male+1)+"_"+pname+"_"+str(followee_count)+pextention[1]
                                saved_count_male+=1
                                    
                            if followee.get_user_gender()==2:
                                p_full_path=save_pic_dir2+str(saved_count_emale+1)+"_"+pname+"_"+str(followee_count)+pextention[1]
                                saved_count_emale+=1
                                
                        p = open(p_full_path, "wb");
                        p.write(pic)
                        p.close()
                            
                        count+=1
                        print "female: "+str(saved_count_female)+"  "+"male: "+str(saved_count_male)+"  "+"emale: "+str(saved_count_emale)
                        if count>limit_count:
                            flag=False
                            break  
                    except:
                        IO_error_count+=1;
                        print "IO error"                    
                print " "              
            except:
                print "why????????????????????"
        else:
            break

if __name__ == '__main__':
    main()

